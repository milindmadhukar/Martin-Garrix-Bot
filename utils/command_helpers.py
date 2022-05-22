import disnake
import random
from .database.user import User
import psutil
import platform

from disnake.ext.commands import (
    MissingPermissions,
    BotMissingPermissions,
    MissingRole,
    MissingAnyRole,
    BotMissingRole,
    BotMissingAnyRole,
    MemberNotFound,
    CommandNotFound,
    CheckFailure,
    PrivateMessageOnly,
    CommandOnCooldown,
    BadUnionArgument,
    ConversionError,
    NoPrivateMessage,
    MissingRequiredArgument,
)

__all = (
    "get_eightball_embed",
    "get_messages_embed",
    "get_whois_embed",
    "get_serverinfo_embed",
    "get_info_embed",
    "get_lyrics_embed",
    "get_error_message",
)


def get_error_message(error) -> str:
    msg = None
    if isinstance(error, BotMissingPermissions):
        msg = f"The bot is missing these permissions to do this command:\n{error.missing_permissions}"

    elif isinstance(error, MissingPermissions):
        msg = f"You are missing these permissions to do this command."

    elif isinstance(
        error,
        (
            BadUnionArgument,
            CommandOnCooldown,
            PrivateMessageOnly,
            NoPrivateMessage,
            MissingRequiredArgument,
            ConversionError,
        ),
    ):
        msg = str(error)

    elif isinstance(error, (BotMissingAnyRole, BotMissingRole)):
        msg = f"I am missing these roles to do this command: \n{error.missing_roles or [error.missing_role]}"

    elif isinstance(error, (MissingRole, MissingAnyRole)):
        msg = f"I am missing these roles to do this command: \n{error.missing_roles or [error.missing_role]}"

    elif isinstance(error, CommandNotFound):
        msg = str(error)

    elif isinstance(error, MemberNotFound):
        msg = str(error)

    elif isinstance(error, CheckFailure):
        msg = f"You are missing these permissions to do this command."

    return msg


def get_eightball_embed(question: str) -> disnake.Embed:
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
    return (
        disnake.Embed(title="The Magic 8 Ball \U0001F3B1 replies")
        .add_field(name="Question", value=question, inline=False)
        .add_field(name="Answer", value=random.choice(responses), inline=False)
    )


def get_messages_embed(member: disnake.Member, msg_count: int) -> disnake.Embed:
    embed = disnake.Embed(color=disnake.Color.orange())
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.add_field(name="Count", value=msg_count)
    embed.set_footer(text=f"User ID: {member.id}")
    return embed


def get_whois_embed(member: disnake.Member, user: User) -> disnake.Embed:
    perm_list = [perm[0] for perm in member.guild_permissions if perm[1]]
    perms_list = [perm.replace("_", " ").title() for perm in perm_list]
    perms = ", ".join(perms_list)

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

    return embed


def get_serverinfo_embed(guild: disnake.Guild) -> disnake.Embed:
    embed = disnake.Embed(title=guild.name, colour=disnake.Colour.blue())
    embed.add_field(name="Owner", value=guild.owner.mention)
    embed.add_field(
        name="Created At", value=guild.created_at.strftime("%b %d %Y, %H:%M:%S")
    )
    embed.add_field(name="Members", value=str(guild.member_count))
    embed.add_field(name="Categories", value=str(len(guild.categories)))
    embed.add_field(name="Text Channels", value=str(len(guild.text_channels)))
    embed.add_field(name="Voice Channels", value=str(len(guild.voice_channels)))
    embed.add_field(name="Roles", value=str(len(guild.roles)))
    embed.add_field(name="Boosters", value=str(guild.premium_subscription_count))
    embed.add_field(
        name="File Size Limit",
        value=str(guild.filesize_limit // (1024 * 1024)) + "mb",
    )
    embed.set_footer(text=f"Guild ID : {guild.id}")
    if guild.icon is not None:
        embed.set_thumbnail(url=guild.icon.url)

    return embed


async def get_info_embed(bot) -> disnake.Embed:
    guild = bot.guild
    platform_details = platform.platform()
    users = await bot.database.fetchrow("""SELECT COUNT(*) FROM users""")
    users = users["count"]
    milind = guild.get_member(421608483629301772)
    korta = guild.get_member(736820906604888096)
    if milind is None:
        milind = "Milind Madhukar"
    else:
        milind = milind.mention
    if korta is None:
        korta = "Korta Po"
    else:
        korta = korta.mention
    cpu_usage = f"{psutil.cpu_percent()}%"
    ram_usage = f"{psutil.virtual_memory().percent}%"
    embed = disnake.Embed(
        title=f"{bot.user.name}!",
        description="A multipurpose bot created exclusively for Garrixers.",
        colour=disnake.Colour.blurple(),
    )
    embed.add_field(name="Creator", value=f"{milind}", inline=False)
    embed.add_field(name="Contributor", value=f"{korta}", inline=False)
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

    return embed


def get_lyrics_embed(song_data) -> disnake.Embed:
    embed = disnake.Embed(
        title=f'{song_data["alias"]} - {song_data["name"]}',
        description=song_data["lyrics"][:4096],
        color=disnake.Colour.orange(),
    )

    if song_data["thumbnail_url"] is not None:
        embed.set_thumbnail(url=song_data["thumbnail_url"])

    return embed
