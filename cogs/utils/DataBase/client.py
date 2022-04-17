import asyncpg
import asyncio

from .message import Message
from .tag import Tag
from .channel import Channel
from .user import User


class DataBase(object):
    def __init__(self, bot, pool, loop=None, timeout: float = 60.0):
        self.bot = bot
        self._pool = pool
        self._loop = loop or asyncio
        self.timeout = timeout
        self._rate_limit = asyncio.Semaphore(value=self._pool._maxsize, loop=self._loop)

    @classmethod
    async def create_pool(cls, bot, uri=None, *, min_connections=10, max_connections=20,
                          timeout=60.0, loop=None, **kwargs):
        pool = await asyncpg.create_pool(uri, min_size=min_connections, max_size=max_connections, **kwargs)
        self = cls(bot=bot, pool=pool, loop=loop, timeout=timeout)
        print('Established DataBase pool with {} - {} connections\n'.format(min_connections, max_connections))
        return self

    async def fetch(self, query, *args):
        async with self._rate_limit:
            async with self._pool.acquire() as con:
                return await con.fetch(query, *args, timeout=self.timeout)

    async def fetchrow(self, query, *args):
        async with self._rate_limit:
            async with self._pool.acquire() as con:
                return await con.fetchrow(query, *args, timeout=self.timeout)

    async def execute(self, query: str, *args):
        async with self._rate_limit:
            async with self._pool.acquire() as con:
                return await con.execute(query, *args, timeout=self.timeout)

    async def get_user(self, user_id: int, guild_id: int):
        query = """SELECT * FROM users WHERE id = $1 AND guild_id = $2"""
        record = await self.fetchrow(query, user_id, guild_id)
        if record is None:
            # Post new user.
            user = User(bot=self.bot, id=user_id, guild_id=guild_id)
            await user.post()
            return user
        return User(bot=self.bot, **record)

    async def get_message(self, message_id: int) -> Message:
        query = """SELECT * FROM messages WHERE message_id = $1"""
        record = await self.fetchrow(query, message_id)
        return Message(bot=self.bot, **record)

    async def get_tag(self, guild_id: int, name: str):
        query = """SELECT * FROM tags WHERE guild_id = $1 AND name = $2"""
        record = await self.fetchrow(query, guild_id, name)
        if record is not None:
            return Tag(bot=self.bot, **record)
        return record

    async def get_channel(self, channel_id: int):
        query = """SELECT * FROM channels WHERE channel_id = $1"""
        record = await self.fetchrow(query, channel_id)
        if record is not None:
            return Channel(bot=self.bot, **record)
        return record

    async def add_mod_role(self, mod_role_id, guild_id):
        query = """UPDATE mod_roles SET role_id = $1 WHERE guild_id = $2"""
        await self.execute(query, mod_role_id, guild_id)

    async def add_admin_role(self, admin_role_id, guild_id):
        query = """UPDATE admin_roles SET role_id = $1 WHERE guild_id = $2"""
        await self.execute(query, admin_role_id, guild_id)

    async def remove_mod_role(self, mod_role_id, guild_id):
        query = """DELETE FROM mod_roles WHERE role_id = $1 & guild_id = $2"""
        await self.execute(query, mod_role_id, guild_id)

    async def remove_admin_role(self, mod_role_id, guild_id):
        query = """DELETE FROM admin_roles WHERE role_id = $1 & guild_id = $2"""
        await self.execute(query, mod_role_id, guild_id)


