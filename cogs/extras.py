from datetime import datetime
import typing

import discord
from discord.ext import commands, tasks

from core.MartinBotBase import MartinGarrixBot
from utils.checks import is_admin_check, is_milind_check
from utils.command_helpers import (
    get_eightball_embed,
    get_info_embed,
    get_messages_embed,
    get_serverinfo_embed,
    get_whois_embed,
)
from utils.helpers import success_embed


# TODO: Fill in all the descriptions
class Extras(commands.Cog):
    def __init__(self, bot: MartinGarrixBot):
        self.bot = bot

    async def cog_load(self) -> None:
        pass
        # self.change_status.start()

    @tasks.loop(minutes=2)
    async def change_status(self):
        await self.bot.wait_until_ready()
        status = await self.bot.database.fetchrow(
            "SELECT alias, name FROM songs ORDER BY RANDOM() LIMIT 1"
        )
        if status is None:
            return
        alias = status.get("alias", "Martin Garrix")
        name = status.get("name", "High On Life")
        status = f"{alias}  - {name}"
        if len(status) >= 16:
            status = name
        await self.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name=status)
        )

    @commands.hybrid_command(
        name="8ball",
        aliases=["eightball"],
        help="8 ball command to make decisions",
    )
    async def eightball(self, ctx: commands.Context, *, question: str):
        print("")
        return await ctx.send(embed=get_eightball_embed(question))

    @commands.hybrid_command(
        name="ping",
        help="Check the latency of the bot from the server.",
        aliases=["latency"],
    )
    async def ping(self, ctx: commands.Context):
        await ctx.send(
            f"**Pong! {round(self.bot.latency * 1000)}ms** \U0001F3D3", ephemeral=True
        )

    @commands.hybrid_command(
        name="avatar",
        help="Get the avatar of a member.",
    )
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=str(member), color=member.color)
        embed.set_image(url=member.display_avatar.with_size(512).url)
        return await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="messages", help="Get the total number of messages sent by a member."
    )
    async def messages(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        query = "SELECT messages_sent FROM users WHERE id = $1"
        msg_count = await self.bot.database.fetchrow(query, member.id)
        messages = msg_count["messages_sent"]

        await ctx.send(embed=get_messages_embed(member, messages))

    @commands.hybrid_command(
        name="whois",
        help="Get the info about a member or bot in the server.",
    )
    async def whois(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        user = await self.bot.database.get_user(member.id) if not member.bot else None
        return await ctx.send(embed=get_whois_embed(member, user))

    @commands.check_any(is_admin_check(), is_milind_check())
    @commands.hybrid_command(
        name="embed",
        help="Command to create an embed in the chat.",
    )
    async def embed(
        self,
        ctx: commands.Context,
        channel: typing.Optional[discord.TextChannel] = None,
        title: str = None,
        *,
        description: str = None,
    ):
        if ctx.interaction is None:
            await ctx.message.delete()
        embed = discord.Embed(title=title, colour=discord.Colour.blurple())
        if description is not None:
            embed.description = description
        channel = channel or ctx.channel
        await channel.send(embed=embed)

        return await ctx.send(
            embed=await success_embed("Successfully sent the message."),
            ephemeral=True,
            delete_after=10,
        )

    @commands.check_any(is_admin_check(), is_milind_check())
    @commands.hybrid_command(
        name="say",
        help="Send a message in a channel.",
    )
    async def say(
        self,
        ctx: commands.Context,
        channel: typing.Optional[discord.TextChannel] = None,
        *,
        message: str = None,
    ):
        if ctx.interaction is None:
            await ctx.message.delete()

        channel = channel or ctx.channel
        await channel.send(message)

        return await ctx.send(
            embed=await success_embed("Successfully sent the message."),
            ephemeral=True,
            delete_after=10,
        )

    @commands.hybrid_command(
        name="serverinfo", help="Gives you the info of the current server."
    )
    async def serverinfo(self, ctx: commands.Context):
        guild: discord.Guild = self.bot.guild
        return await ctx.send(embed=get_serverinfo_embed(guild))

    @commands.hybrid_command(
        name="info", help="Gives you the info about the bot and its creator."
    )
    async def info(self, ctx: commands.Context):
        return await ctx.send(embed=await get_info_embed(self.bot))

    @is_milind_check()
    @commands.command(
        name="recover"
    )
    async def recover(self, ctx: commands.Context):
        guild: discord.Guild = self.bot.guild
        channels = guild.channels

        for channel in channels:
            # Get all messages in the channel until timestamp
            messages = channel.history(limit=1000000, after=datetime.fromtimestamp(1699479631))
            print(f"Channel: {channel.name}", "Messages: ", len(messages))

            for message in messages:
                if message.author.bot:
                    continue

                query = """INSERT INTO messages ( message_id, channel_id, author_id, content, timestamp)
                           VALUES ( $1, $2, $3, $4, $5 )
                           ON CONFLICT DO NOTHING"""
                await self.bot.database.execute(
                    query, message.id, message.channel.id, message.author.id, message.content, message.created_at
                )

                await self.bot.database.execute(
                    "UPDATE users SET messages_sent = messages_sent + 1 WHERE id = $1", message.author.id
                )


async def setup(bot):
    await bot.add_cog(Extras(bot))
