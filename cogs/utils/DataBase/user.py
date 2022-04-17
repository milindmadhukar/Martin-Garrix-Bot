from datetime import datetime


class User(object):
    def __init__(self, bot,
                 id: int,
                 guild_id: int,
                 messages_sent: int = 0,
                 total_xp: int = 0,
                 last_xp_added: datetime = None,
                 in_hand: int = 0,
                 garrix_coins: int = 0):
        self.bot = bot
        self.id = id
        self.guild_id = guild_id
        self.messages_sent = messages_sent
        self.total_xp = total_xp
        self.last_xp_added = last_xp_added
        self.in_hand = in_hand
        self.garrix_coins = garrix_coins

    async def post(self) -> None:
        query = """SELECT * FROM users WHERE id = $1 AND guild_id = $2"""
        assure_exclusive = await self.bot.db.fetch(query, self.id, self.guild_id)
        if len(assure_exclusive) == 0:
            query = """INSERT INTO users (id, guild_id)
                    VALUES ( $1, $2 )
                    ON CONFLICT DO NOTHING"""
            await self.bot.db.execute(query, self.id, self.guild_id)

    async def update_garrix_coins(self) -> None:
        query = """UPDATE users SET garrix_coins = $1 WHERE id = $2 AND guild_id = $3"""
        await self.bot.db.execute(query, self.garrix_coins, self.id, self.guild_id)
