import disnake
from disnake.ext.commands.core import command
from disnake.ext import commands, tasks
import typing

from utils.checks import is_admin_check, is_milind_check
from core.MartinBotBase import MartinGarrixBot

from utils.command_helpers import (
    get_eightball_embed,
    get_info_embed,
    get_messages_embed,
    get_serverinfo_embed,
    get_whois_embed,
)
from utils.helpers import success_embed


class Extras(commands.Cog):
    def __init__(self, bot: MartinGarrixBot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.change_status.start()

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
            activity=disnake.Activity(type=disnake.ActivityType.listening, name=status)
        )

    @commands.command(
        help="8 ball command to make decisions",
        aliases=["8ball", "magicball"],
    )
    async def eightball(self, ctx: commands.Context, *, question: str):
        return await ctx.send(embed=get_eightball_embed(question))

    @commands.slash_command(
        name="8ball",
        description="8 ball command to make decisions",
    )
    async def eightball_slash(
        self,
        inter: disnake.ApplicationCommandInteraction,
        question: str = commands.Param(
            description="Enter your question to ask the magic 8 ball."
        ),
    ):
        return await inter.response.send_message(embed=get_eightball_embed(question))

    @commands.command(
        help="Check the latency of the bot from the server.", aliases=["latency"]
    )
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"**Pong! {round(self.bot.latency * 1000)}ms** \U0001F3D3")

    @commands.slash_command(
        name="ping", description="Check the latency of the bot from the server."
    )
    async def ping_slash(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(
            f"**Pong! {round(self.bot.latency * 1000)}ms** \U0001F3D3"
        )

    @commands.command(
        help="Get the avatar of a member.",
        aliases=["av", "pfp", "profilepic", "profilepicture"],
    )
    async def avatar(self, ctx: commands.Context, member: disnake.Member = None):
        member = member or ctx.author
        embed = disnake.Embed(title=str(member), color=member.color)
        embed.set_image(url=member.display_avatar.with_size(512).url)
        await ctx.send(embed=embed)

    @commands.slash_command(name="avatar", description="Get the avatar of a member.")
    async def avatar_slash(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: typing.Optional[disnake.Member] = commands.Param(
            None, description="Enter the member whose avatar you wanna see."
        ),
    ):
        member = member or inter.author
        embed = disnake.Embed(title=str(member), color=member.color)
        embed.set_image(url=member.display_avatar.with_size(512).url)
        return await inter.response.send_message(embed=embed)

    @commands.command(help="Get the total number of messages sent by a member.")
    async def messages(self, ctx: commands.Context, member: disnake.Member = None):
        member = member or ctx.author
        query = "SELECT messages_sent FROM users WHERE id = $1"
        msg_count = await self.bot.database.fetchrow(query, member.id)
        messages = msg_count["messages_sent"]

        await ctx.send(embed=get_messages_embed(member, messages))

    @commands.slash_command(
        name="messages",
        description="Get the total number of messages sent by a member.",
    )
    async def messages_slash(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: typing.Optional[disnake.Member] = commands.Param(
            None, description="Enter the member whose message count you want to see,"
        ),
    ):
        member = member or inter.author
        query = "SELECT messages_sent FROM users WHERE id = $1"
        msg_count = await self.bot.database.fetchrow(query, member.id)
        messages = msg_count["messages_sent"]

        await inter.response.send_message(embed=get_messages_embed(member, messages))

    @commands.command(
        help="Get the info about a member or bot in the server.", aliases=["memberinfo"]
    )
    async def whois(self, ctx: commands.Context, member: disnake.Member = None):
        member = member or ctx.author
        user = await self.bot.database.get_user(member.id) if not member.bot else None
        return await ctx.send(embed=get_whois_embed(member, user))

    @commands.slash_command(
        name="whois", description="Get the info about a member or bot in the server."
    )
    async def whois_slash(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: typing.Optional[disnake.Member] = commands.Param(
            None, description="Enter the member whose info you need."
        ),
    ):
        member = member or inter.author
        user = await self.bot.database.get_user(member.id) if not member.bot else None

        return await inter.send(embed=get_whois_embed(member, user))

    @commands.check_any(is_admin_check(), is_milind_check())
    @commands.command(help="Command to create an embed in the chat.", aliases=["em"])
    async def embed(
        self, ctx: commands.Context, title: str, *, description: str = None
    ):
        await ctx.message.delete()
        embed = disnake.Embed(title=title, colour=disnake.Colour.blurple())
        if description is not None:
            embed.description = description
        await ctx.send(embed=embed)

        return await ctx.send(embed=await success_embed("Successfully sent the message."))

    @commands.check_any(is_admin_check(), is_milind_check())
    @commands.slash_command(
        name="embed", description="Command to create an embed in the chat."
    )
    async def embed_slash(
        self,
        inter: disnake.ApplicationCommandInteraction,
        channel: typing.Optional[disnake.TextChannel] = commands.Param(
            None, description="Enter the channel to send the embed in."
        ),
        title: str = commands.Param(description="Enter the title of the embed."),
        description: typing.Optional[str] = commands.Param(
            None, description="Enter the description of the embed."
        ),
    ):
        embed = disnake.Embed(title=title, colour=disnake.Colour.blurple())
        if description is not None:
            embed.description = description
        channel = channel or inter.channel
        await channel.send(embed=embed)

        return await inter.response.send_message(embed=await success_embed("Successfully sent the message."), ephemeral=True)

    @commands.check_any(is_admin_check(), is_milind_check())
    @commands.command(help="Send a message in a channel.", aliases=["send"])
    async def say(self, ctx, channel: disnake.TextChannel, *, message: str = None):
        if message is None:
            await ctx.send("Please provide a message.")
        message = await commands.clean_content().convert(ctx=ctx, argument=message)
        await channel.send(message)
        return await ctx.send(embed=await success_embed("Successfully sent the message."), delete_after=10)

    @commands.check_any(is_admin_check(), is_milind_check())
    @commands.slash_command(name="say", description="Send a message in a channel.")
    async def say_slash(
        self,
        inter: disnake.ApplicationCommandInteraction,
        channel: typing.Optional[disnake.TextChannel] = commands.Param(
            None, description="Enter the channel you want to send the message in."
        ),
        message: str = commands.Param(
            description="Enter your message to send in the channel"
        ),
    ):
        # message = await commands.clean_content().convert(ctx=inter, argument=message)
        channel = channel or inter.channel
        await channel.send(message)

        return await inter.response.send_message(embed=await success_embed("Successfully sent the message."), ephemeral=True)

    @commands.command(help="Gives you the info of the current server.")
    async def serverinfo(self, ctx: commands.Context):
        guild: disnake.Guild = self.bot.guild
        return await ctx.send(embed=get_serverinfo_embed(guild))

    @commands.slash_command(name="serverinfo", description="Gives you the info of the current server.")
    async def serverinfo_slash(self, inter: disnake.ApplicationCommandInteraction):
        guild: disnake.Guild = self.bot.guild
        return await inter.response.send_message(embed=get_serverinfo_embed(guild))

    @commands.command(help="Gives you the info about the bot and its creator.")
    async def info(self, ctx: commands.Context):
        bot = self.bot
        embed = await get_info_embed(bot)
        return await ctx.send(embed=embed)

    @commands.slash_command(name="info", description="Gives you the info about the bot and its creator.")
    async def info_slash(self, inter: disnake.ApplicationCommandInteraction):
        bot = self.bot
        embed = await get_info_embed(bot)
        return await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Extras(bot))
