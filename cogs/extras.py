import disnake
import psutil
from disnake.ext import commands, tasks
import random
import platform

from core.MartinBotBase import MartinGarrixBot


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
        print(self.bot.database)
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
        aliases=["8ball", "magicball", "eightball"],
    )
    async def _8ball(self, ctx: commands.Context, *, question: str):
        responses = [
            "As I see it, yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don’t count on it.",
            "It is certain.",
            "It is decidedly so.",
            "Most likely.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Outlook good.",
            "Reply hazy, try again.",
            "Signs point to yes.",
            "Very doubtful.",
            "Without a doubt.",
            "Yes.",
            "Yes – definitely.",
            "You may rely on it.",
        ]
        embed = (
            disnake.Embed(title="The Magic 8 Ball \U0001F3B1 replies")
            .add_field(name="Question", value=question, inline=False)
            .add_field(name="Answer", value=random.choice(responses), inline=False)
        )

        return await ctx.send(embed=embed)

    @commands.command(
        help="Check the latency of the bot from the server.", aliases=["latency"]
    )
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"**Pong! {round(self.bot.latency * 1000)}ms** \U0001F3D3")

    @commands.command(
        help="Get the avatar of a member.",
        aliases=["av", "pfp", "profilepic", "profilepicture"],
    )
    async def avatar(self, ctx: commands.Context, member: disnake.Member = None):
        member = member or ctx.author
        embed = disnake.Embed(title=str(member), color=member.color)
        embed.set_image(url=member.display_avatar.with_size(512).url)
        await ctx.send(embed=embed)

    @commands.command(help="Get the total number of messages sent by a member.")
    async def messages(self, ctx: commands.Context, member: disnake.Member = None):
        member = member or ctx.author
        query = "SELECT messages_sent FROM users WHERE id = $1"
        msg_count = await self.bot.database.fetchrow(query, member.id)
        embed = disnake.Embed(color=disnake.Color.orange())
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.add_field(name="Count", value=msg_count["messages_sent"])
        embed.set_footer(text=f"User ID: {member.id}")
        await ctx.send(embed=embed)

    @commands.command(
        help="Get the info about a member or bot in the server.", aliases=["memberinfo"]
    )
    async def whois(self, ctx: commands.Context, member: disnake.Member = None):
        member = member or ctx.author

        perm_list = [perm[0] for perm in member.guild_permissions if perm[1]]
        perms_list = [perm.replace("_", " ").title() for perm in perm_list]
        perms = ", ".join(perms_list)

        user = await self.bot.database.get_user(member.id) if not member.bot else None
        embed = disnake.Embed(description=f"{member.mention}", color=member.color)
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        if user is not None:
            embed.add_field(name="Messages sent", value=user.messages_sent)
            embed.add_field(name="Status", value=f"{str(member.status).upper()}")
            embed.add_field(name="Nickname", value=member.nick, inline=True)

        embed.add_field(
            name="Joined",
            value=member.joined_at.strftime("%b %d %Y, %H:%M:%S"),
            inline=False,
        )
        embed.add_field(
            name="Registered",
            value=member.created_at.strftime("%b %d %Y, %H:%M:%S"),
            inline=False,
        )
        roles = member.roles[:0:-1]
        embed.add_field(
            name=f"Roles [{len(roles)}]",
            value=" ".join([role.mention for role in roles]) or "None",
            inline=False,
        )

        embed.add_field(name=f"Permissions", value=f"{perms}", inline=False)

        embed.set_thumbnail(url=member.display_avatar.with_size(256).url)
        embed.set_footer(text=f"ID: {member.id}")
        return await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.command(help="Command to create an embed in the chat.", aliases=["em"])
    async def embed(
        self, ctx: commands.Context, title: str, *, description: str = None
    ):
        await ctx.message.delete()
        embed = disnake.Embed(title=title, colour=disnake.Colour.blurple())
        if description is not None:
            embed.description = description
        return await ctx.send(embed=embed)

    @commands.command(help="Send a message in a channel.", aliases=["send"])
    @commands.has_permissions(administrator=True)
    async def say(self, ctx, channel: disnake.TextChannel, *, message: str = None):
        if message is None:
            await ctx.send("Please provide a message.")
        message = await commands.clean_content().convert(ctx=ctx, argument=message)
        await channel.send(message)
        # TODO: Some sort of response?

    @commands.command(help="Gives you the info of the current server.")
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        embed = disnake.Embed(title=guild.name, colour=disnake.Colour.blue())
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=guild.owner.mention)
        embed.add_field(name="Members", value=str(guild.member_count))
        embed.add_field(name="Region", value=str(guild.region).title())
        embed.add_field(name="Categories", value=str(len(guild.categories)))
        embed.add_field(name="Roles", value=str(len(guild.roles)))
        embed.add_field(name="Boosters", value=str(guild.premium_subscription_count))
        embed.add_field(name="Text Channels", value=str(len(guild.text_channels)))
        embed.add_field(name="Voice Channels", value=str(len(guild.voice_channels)))
        embed.add_field(
            name="Created At", value=guild.created_at.strftime("%b %d %Y, %H:%M:%S")
        )
        embed.set_footer(text=f"Guild ID : {guild.id}")
        return await ctx.send(embed=embed)

    @commands.command(help="Gives you the info about the bot and its creator.")
    async def info(self, ctx: commands.Context):
        bot = self.bot
        platform_details = platform.platform()
        users = await self.bot.database.fetchrow("""SELECT COUNT(*) FROM users""")
        users = users["count"]
        milind = ctx.guild.get_member(421608483629301772)
        if milind is None:
            milind = "Milind Madhukar"
        else:
            milind = milind.mention
        cpu_usage = f"{psutil.cpu_percent()}%"
        ram_usage = f"{psutil.virtual_memory().percent}%"
        embed = disnake.Embed(
            title=f"{bot.user.name}!",
            description="A multipurpose bot created exclusively for Garrixers.",
            colour=disnake.Colour.blurple(),
        )
        embed.add_field(name="Creator", value=f"{milind}", inline=False)
        embed.add_field(name="Total Users", value=users, inline=False)
        embed.add_field(
            name="Created At", value=bot.user.created_at.strftime("%b %d %Y, %H:%M:%S")
        )
        embed.add_field(
            name="Bot Server Info",
            value=f"**Platform:** {platform_details}\n\n**CPU Usage:** {cpu_usage}\n**Ram Usage:** {ram_usage}",
            inline=False,
        )
        embed.set_footer(
            text="Please note that this bot is completely fan made.\nIt "
            "does not affiliate with Martin Garrix or STMPD RCRDS in any way."
        )
        embed.set_image(url=bot.user.display_avatar.url)

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Extras(bot))
