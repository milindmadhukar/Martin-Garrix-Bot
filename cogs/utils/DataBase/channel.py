class Channel(object):
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id

    async def post(self):
        query = """INSERT INTO channels ( id )
                   VALUES ( $1 ) ON CONFLICT DO NOTHING"""
        await self.bot.db.execute(query, self.channel_id)

    async def update(self, channel_id):
        query = """UPDATE channels SET id = $1 WHERE id = $2"""
        await self.bot.db.execute(query, channel_id, self.channel_id)
        self.channel_id = channel_id

    async def delete(self, channel_id):
        query = """DELETE FROM channels WHERE id = $1 IF EXISTS"""
        await self.bot.db.execute(query, self.channel_id)
