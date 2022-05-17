#  -*- coding: utf-8 -*-
import datetime
import os
import pkgutil
import sys
import traceback
import typing
from typing import Optional

import disnake
import dotenv
from aiohttp import ClientSession
from disnake import AllowedMentions, Intents, Message
from disnake.ext import commands
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

from utils import failure_embed
from utils.database import Message
from utils.database.client import Database
from utils.enums import Config
from utils.helpcommand import HelpCommand


class MartinGarrixBot(commands.Bot):
    """
    A subclass of `commands.Bot` with additional features.
    """

    def __init__(self, *args, **kwargs):
        dotenv.load_dotenv(".env")

        super().__init__(
            command_prefix=commands.when_mentioned_or("m.", "M.", "mg.", "Mg.", "MG."),
            intents=Intents.all(),
            allowed_mentions=AllowedMentions(everyone=True, roles=True),
            case_insensitive=True,
            sync_commands_debug=True,
            help_command=HelpCommand(),
            enable_debug_events=True,
            reload=True,  # This Kwarg Enables Cog watchdog, Hot reloading of cogs.
            *args,
            **kwargs,
        )

        self.session: Optional[ClientSession] = None
        self.start_time = disnake.utils.utcnow()
        self.bot_config = Config
        self.database: typing.Optional[Database] = None

    def load_cogs(self, exts: typing.Iterable[str]) -> None:
        """
        This method loads all the cogs to the bot from the specified folder.

        Parameters:
            exts (Iterable[list]): A list of extensions to load.
        """

        for m in pkgutil.iter_modules(exts):
            # a much better way to load cogs
            module = f"cogs.{m.name}"
            try:
                self.load_extension(module)
                print(f"Loaded extension '{m.name}'")
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        self.load_extension("jishaku")
        print(f"Loaded extension 'jishaku'")

    def set_configuration_attributes(self):
        self.guild = self.get_guild(self.bot_config.GUILD_ID.value)
        if self.guild is None:
            print("Could not find guild.")
        self.modlogs_channel = (
            self.get_channel(self.bot_config.MODLOGS_CHANNEL.value)
            if self.bot_config.MODLOGS_CHANNEL is not None
            else None
        )
        self.leave_join_logs_channel = (
            self.get_channel(self.bot_config.LEAVE_JOIN_LOGS_CHANNEL.value)
            if self.bot_config.LEAVE_JOIN_LOGS_CHANNEL is not None
            else None
        )
        self.youtube_notifications_channel = (
            self.get_channel(self.bot_config.YOUTUBE_NOTIFICATION_CHANNEL.value)
            if self.bot_config.YOUTUBE_NOTIFICATION_CHANNEL is not None
            else None
        )
        self.reddit_notifications_channel = (
            
            self.get_channel(self.bot_config.REDDIT_NOTIFICATION_CHANNEL.value)
            if self.bot_config.REDDIT_NOTIFICATION_CHANNEL is not None
            else None
        )
        self.welcomes_channel = (
            self.get_channel(self.bot_config.WELCOMES_CHANNEL.value)
            if self.bot_config.WELCOMES_CHANNEL is not None
            else None
        )
        self.delete_logs_channel = (
            self.get_channel(self.bot_config.DELETE_LOGS_CHANNEL.value)
            if self.bot_config.DELETE_LOGS_CHANNEL is not None
            else None
        )
        self.edit_logs_channel = (
            self.get_channel(self.bot_config.EDIT_LOGS_CHANNEL.value)
            if self.bot_config.EDIT_LOGS_CHANNEL is not None
            else None
        )
        self.team_role = self.guild.get_role(self.bot_config.TEAM_ROLE.value)
        self.support_role = self.guild.get_role(self.bot_config.SUPPORT_ROLE.value)
        self.moderator_role = self.guild.get_role(self.bot_config.MODERATOR_ROLE.value)
        self.admin_role = self.guild.get_role(self.bot_config.ADMIN_ROLE.value)
        self.garrixer_role = self.guild.get_role(self.bot_config.GARRXIER_ROLE.value)
        self.true_garrixer_role = self.guild.get_role(
            self.bot_config.TRUE_GARRIXER_ROLE.value
        )
        self.reddit_notifications_role = self.guild.get_role(
            self.bot_config.REDDIT_NOTIFICATION_ROLE.value
        )
        self.garrix_news_role = self.guild.get_role(
            self.bot_config.GARRIX_NEWS_ROLE.value
        )
        self.xp_multiplier = self.bot_config.XP_MULTIPLIER.value

    async def on_ready(self):
        """
        This function is triggered when the bot is connected properly to gateway and the bot cache is evenly populated.
        """
        await self.wait_until_ready()
        self.set_configuration_attributes()
        print(
            f"----------Bot Initialization.-------------\n"
            f"Bot name: {self.user.name}\n"
            f"Bot ID: {self.user.id}\n"
            f"Total Guilds: {len(self.guilds)}\n"
            f"Total Users: {len(self.users)}\n"
            f"------------------------------------------"
        )

    async def on_message(self, message: disnake.Message):
        await self.wait_until_ready()
        if not message.guild:
            return
        elif message.guild.id != self.guild.id:
            return
        await Message.on_message(
            bot=self, message=message, xp_multiplier=self.xp_multiplier
        )
        return await self.process_commands(message)

    async def on_message_delete(self, message: disnake.Member):
        if message.embeds or message.author.bot:
            return
        if self.delete_logs_channel is not None:
            embed = disnake.Embed(
                description=f"Message deleted by {message.author.mention} in {message.channel.mention}",
                color=disnake.Color.dark_orange(),
            )
            embed.add_field(name="Content", value=message.content)
            await self.delete_logs_channel.send(embed=embed)

    async def on_message_edit(
        self, message_before: disnake.Message, message_after: disnake.Message
    ):
        if message_before.embeds or message_after.embeds:
            return
        if message_before.author.bot or message_after.author.bot:
            return

        await Message.on_message(
            bot=self, message=message_after, xp_multiplier=self.xp_multiplier
        )
        if self.edit_logs_channel is not None:
            embed = disnake.Embed(
                description=f"Message edited by {message_before.author.mention} in {message_before.channel.mention}",
                color=disnake.Color.gold(),
            )
            embed.add_field(name="Original Message", value=f"{message_before.content}")
            embed.add_field(
                name="Edited Message",
                value=f"{message_after.content}\n[Go to message]({message_after.jump_url})",
            )
            await self.edit_logs_channel.send(embed=embed)

    async def on_command_error(self, ctx: commands.Context, error):
        if hasattr(ctx.command, "on_error"):
            return

        elif isinstance(error, BotMissingPermissions):
            message = await ctx.send(
                f"The bot is missing these permissions to do this command:\n{error.missing_permissions}"
            )

        elif isinstance(error, MissingPermissions):
            message = await ctx.send(
                f"You are missing these permissions to do this command."
            )

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
            message = await ctx.send(str(error))

        elif isinstance(error, (BotMissingAnyRole, BotMissingRole)):
            message = await ctx.send(
                f"I am missing these roles to do this command: \n{error.missing_roles or [error.missing_role]}"
            )

        elif isinstance(error, (MissingRole, MissingAnyRole)):
            message = await ctx.send(
                f"I am missing these roles to do this command: \n{error.missing_roles or [error.missing_role]}"
            )

        elif isinstance(error, CommandNotFound):
            message = await ctx.send(str(error))

        elif isinstance(error, MemberNotFound):
            message = await ctx.send(str(error))

        elif isinstance(error, CheckFailure):
            message = await ctx.send(
                f"You are missing these permissions to do this command."
            )

        else:
            return await self.handle_error(ctx, error)

        await ctx.message.delete(delay=20.0)
        return await message.delete(delay=20.0)

    async def handle_error(self, ctx: commands.Context, error) -> disnake.Message:
        print(error)
        error_channel = self.get_channel(int(os.environ.get("ERROR_CHANNEL")))
        trace = traceback.format_exception(type(error), error, error.__traceback__)
        paginator = commands.Paginator(prefix="", suffix="")

        for line in trace:
            paginator.add_line(line)

        def embed_exception(text: str, *, index: int = 0) -> disnake.Embed:
            embed = disnake.Embed(
                color=disnake.Color(value=15532032),
                description=f"Command that caused the error: {ctx.message.content} from {ctx.author.name}\nError: {error}'"
                + "```py\n%s\n```" % text,
                timestamp=datetime.datetime.utcnow(),
            )

            if not index:
                embed.title = "Error"

            return embed

        for page in paginator.pages:
            await error_channel.send(embed=embed_exception(page))

        return await ctx.send(
            embed=await failure_embed(
                "Some error occurred.",
                "The developer has been informed and should fix it soon.",
            )
        )

    async def on_disconnect(self):
        """
        |coro|
        This function is triggered when the bot is disconnected from the gateway.
        """
        print("Closing Aiohttp ClientSession...")
        await self.session.close()
        return

    async def create_database_connection_pool(self):
        """
        |coro|
        This method creates a postgres database connection and executes sql code in it.
        """
        self.database = await Database.create_pool(
            bot=self, uri=os.environ.get("POSTGRES_URI")
        )

        with open("./static/database.sql", mode="r") as r:
            queries = r.read()

        await self.database.execute(queries)
        return

    async def login(self, *args, **kwargs) -> None:
        """
        This method logins the bot into Discord gateway.
        """

        self.session = ClientSession()  # creating a ClientSession
        await self.create_database_connection_pool()

        await super().login(*args, **kwargs)
