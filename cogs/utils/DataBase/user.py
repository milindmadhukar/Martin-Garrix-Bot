from datetime import datetime

class User(object):
    def __init__(self, bot,
                 id: int,
                 messages_sent: int = 0,
                 total_xp: int = 0,
                 last_xp_added: datetime = None,
                 in_hand: int = 0,
                 garrix_coins: int = 0):
        self.bot = bot
        self.id = id
        self.messages_sent = messages_sent
        self.total_xp = total_xp
        self.last_xp_added = last_xp_added
        self.in_hand = in_hand
        self.garrix_coins = garrix_coins

    async def post(self) -> None:
        query = "SELECT * FROM users WHERE id = $1"
        assure_exclusive = await self.bot.db.fetch(query, self.id)
        if len(assure_exclusive) == 0:
            query = """INSERT INTO users (id)
                    VALUES ( $1 )
                    ON CONFLICT DO NOTHING"""
            await self.bot.db.execute(query, self.id)

    async def add_coins(self, amount:int) -> None:
        query = """UPDATE SET in_hand=in_hand + $2 WHERE id = $1"""
        await self.bot.db.execute(query, self.id, amount)

    async def update_garrix_coins(self) -> None:
        query = """UPDATE users SET in_hand = $1 WHERE id = $2"""
        await self.bot.db.execute(query, self.garrix_coins, self.id)