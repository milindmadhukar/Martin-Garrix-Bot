import asyncpg
import asyncio

from .message import Message
from .tag import Tag
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

    async def get_user(self, id: int):
        query = """SELECT * FROM users WHERE id = $1"""
        record = await self.fetchrow(query, id)
        if record is None:
            # Post new user.
            user = User(bot=self.bot, id=id)
            await user.post()
            return user
        return User(bot=self.bot, **record)

    async def get_message(self, message_id: int) -> Message:
        query = """SELECT * FROM messages WHERE message_id = $1"""
        record = await self.fetchrow(query, message_id)
        return Message(bot=self.bot, **record)

    async def get_tag(self, name: str):
        query = """SELECT * FROM tags WHERE name = $1"""
        record = await self.fetchrow(query, name)
        if record is not None:
            return Tag(bot=self.bot, **record)
        return record