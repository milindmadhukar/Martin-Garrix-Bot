from asyncpg.connection import asyncio
import discord
from discord.ext import commands, tasks

from difflib import SequenceMatcher

from core.MartinBotBase import MartinGarrixBot


class SingAlong(commands.Cog):
    def __init__(self, bot: MartinGarrixBot):
        self.bot = bot
        self.sing_along_channel = bot.sing_along_channel
        if self.sing_along_channel is None:
            print("Mai toh jaara bye")
            return

        # Get a random song

    async def cog_load(self) -> None:
        self.sing_along_role = discord.utils.get(
            self.sing_along_channel.guild.roles, name="Singing Along"
        )
        if self.sing_along_role is None:
            self.sing_along_role = await self.sing_along_channel.guild.create_role(
                name="Singing Along"
            )

        await self.sing_along_channel.set_permissions(
            self.sing_along_role, send_messages=False
        )

        await self.bot.wait_until_ready()
        await self.reset_sing_along()

        self.check_sing_along.start()

    async def reset_sing_along(self):
        await self.sing_along_channel.purge(limit=500)

        query = "SELECT * FROM songs WHERE lyrics IS NOT NULL AND alias = 'Martin Garrix' ORDER BY RANDOM() LIMIT 1"
        song = await self.bot.database.fetchrow(query)

        self.current_song_name = song["name"]
        self.current_song_alias = song["alias"]
        self.current_song_lyrics = song["lyrics"].split("\n")
        self.line_count = len(song["lyrics"].split("\n"))
        self.current_line = 0

        await self.sing_along_channel.send(
            f"## Sing Along with me! {self.current_song_alias} - {self.current_song_name}\nI'll go first."
        )
        await self.sing_along_channel.send(self.current_song_lyrics[self.current_line])

        self.current_line += 1
        self.last_singer = None
        
    @tasks.loop(seconds=45)
    async def check_sing_along(self):
        members = self.sing_along_role.members
        for member in members:
            if member != self.last_singer:
                await member.remove_roles(self.sing_along_role)


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel != self.sing_along_channel:
            return

        if message.author.bot:
            return

        similarity = SequenceMatcher(
            None,
            message.content.lower().replace(" ", ""),
            self.current_song_lyrics[self.current_line].lower().replace(" ", ""),
        ).ratio()

        if similarity is not None and similarity > 0.7 and self.last_singer != message.author:
            self.current_line += 1

            self.last_singer = message.author

            await message.author.add_roles(self.sing_along_role)
            await message.add_reaction("🥳")
            await asyncio.sleep(2)
            await message.remove_reaction("🥳", self.bot.user)

        else:
            await message.add_reaction("❌")
            await asyncio.sleep(1)
            await message.delete()


async def setup(bot):
    await bot.add_cog(SingAlong(bot))
