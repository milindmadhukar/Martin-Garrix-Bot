import asyncio

import asyncpg
from discord.ext import commands

from .message import Message
from .tag import Tag
from .user import User

__all__ = ("Database",)


class Database:
    """
    This class is a database interface for the bot to connect to Postgres.
    """

    def __init__(
        self,
        bot: commands.Bot,
        pool: asyncpg.Pool,
        loop: asyncio.AbstractEventLoop = None,
        timeout: float = 60.0,
    ):
        self.bot = bot
        self._pool = pool
        self._loop = loop or asyncio
        self.timeout = timeout
        self._rate_limit = asyncio.Semaphore(value=self._pool._maxsize)

    @classmethod
    async def create_pool(
        cls,
        bot: commands.Bot,
        uri=None,
        *,
        min_connections=10,
        max_connections=20,
        timeout=60.0,
        loop=None,
        **kwargs,
    ):
        pool = await asyncpg.create_pool(
            uri, min_size=min_connections, max_size=max_connections, **kwargs
        )
        print(
            f"Established DataBase pool with {min_connections} - {max_connections} connections\n"
        )
        return cls(bot=bot, pool=pool, loop=loop, timeout=timeout)

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

    async def get_user(self, id_: int):
        query = """SELECT * FROM users WHERE id = $1"""
        record = await self.fetchrow(query, id_)
        if record is None:
            # Post new user.
            user = User(bot=self.bot, id_=id_)
            await user.post()
            return user
        return User(bot=self.bot, id_=id_, **record)

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
