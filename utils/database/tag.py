from disnake.ext import commands

__all__ = ("Tag",)


class Tag:
    def __init__(
        self,
        bot: commands.Bot,
        creator_id: int,
        content: str,
        name: str,
        uses: int = 0,
        *args,
        **kwargs
    ):

        self.bot = bot
        self.creator_id = creator_id
        self.content = content
        self.name = name.lower()
        self.uses = uses

    async def post(self):
        query = """INSERT INTO tags ( creator_id, content, name, uses)
                   VALUES ( $1, $2, $3, $4)"""
        await self.bot.database.execute(
            query, self.creator_id, self.content, self.name, self.uses
        )
        return

    async def update(self, content: str):
        self.content = content
        query = """UPDATE tags SET content = $2 WHERE name = $1"""
        await self.bot.database.execute(query, self.name, self.content)
        return

    async def delete(self):
        query = """DELETE FROM tags WHERE name = $1"""
        await self.bot.database.execute(query, self.name)
        return

    async def rename(self, new_name: str):
        query = """UPDATE tags SET name = $2 WHERE name = $1"""
        await self.bot.database.execute(query, self.name, new_name)
        return
