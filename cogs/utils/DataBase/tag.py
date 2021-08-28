class Tag:
    def __init__(self, bot, guild_id: int,
                 creator_id: int,
                 content: str,
                 name: str,
                 uses: int = 0,
                 *args, **kwargs):

        self.bot = bot
        self.guild_id = guild_id
        self.creator_id = creator_id
        self.content = content
        self.name = name.lower()
        self.uses = uses

    async def post(self):
        query = """INSERT INTO tags ( guild_id, creator_id, content, name, uses)
                   VALUES ( $1, $2, $3, $4, $5 )"""
        await self.bot.db.execute(query, self.guild_id, self.creator_id, self.content, self.name, self.uses)

    async def update(self, content):
        self.content = content
        query = """UPDATE tags SET content = $2 WHERE guild_id = $1 AND name = $3"""
        await self.bot.db.execute(query, self.guild_id, self.content, self.name)

    async def delete(self):
        query = """DELETE FROM tags WHERE guild_id = $1 AND name = $2"""
        await self.bot.db.execute(query, self.guild_id, self.name)

    async def rename(self, new_name):
        query = """UPDATE tags SET name = $3 WHERE guild_id = $1 AND name = $2"""
        await self.bot.db.execute(query, self.guild_id, self.name, new_name)
