from datetime import datetime
from disnake.ext import commands

__all__ = ("User",)


class User:
    def __init__(
        self,
        bot: commands.Bot,
        id_: int,
        messages_sent: int = 0,
        total_xp: int = 0,
        last_xp_added: datetime = None,
        in_hand: int = 0,
        garrix_coins: int = 0,
        *args,
        **kwargs
    ):
        self.bot = bot
        self.id = id_
        self.messages_sent = messages_sent
        self.total_xp = total_xp
        self.last_xp_added = last_xp_added
        self.in_hand = in_hand
        self.garrix_coins = garrix_coins

    async def post(self) -> None:
        query = "SELECT * FROM users WHERE id = $1"
        assure_exclusive = await self.bot.database.fetch(query, self.id)
        if len(assure_exclusive) == 0:
            query = """INSERT INTO users (id)
                    VALUES ( $1 )
                    ON CONFLICT DO NOTHING"""
            await self.bot.database.execute(query, self.id)
        return

    async def add_coins(self, amount: int) -> None:
        query = """UPDATE users SET in_hand=in_hand + $2 WHERE id = $1"""
        await self.bot.database.execute(query, self.id, amount)
        return

    async def update_garrix_coins(self) -> None:
        query = """UPDATE users SET in_hand = $1 WHERE id = $2"""
        await self.bot.database.execute(query, self.garrix_coins, self.id)
        return
