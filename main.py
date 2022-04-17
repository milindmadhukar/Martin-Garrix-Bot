import datetime

import discord
from discord.ext import commands
from discord.ext.commands.errors import *

import dotenv
import os
import asyncio
import random
import inspect
import traceback

import bot_config
from cogs.utils.DataBase.client import DataBase
from cogs.utils.DataBase.message import Message
from cogs.utils.DataBase import init_db
from cogs.utils.custom_embed import failure_embed

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"

cogs = [
    'cogs.extras',
    'cogs.fun',
    'cogs.help',
    'cogs.levelling',
    'cogs.moderation',
    'cogs.notifications',
    'cogs.polls',
    'cogs.reaction_roles',
    'cogs.setup_guild',
    'cogs.tags',
    'jishaku'
]

class MartinGarrixBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=kwargs.pop('command_prefix', ('m.', 'M.', 'mg.', 'Mg.', 'MG.')),
                         intents=discord.Intents.all(),
                         allowed_mentions=discord.AllowedMentions(everyone=True, roles=True),
                         case_insensetive=True,
                         **kwargs)

        self.modlogs_channel = self.get_channel(id=bot_config.MODLOGS_CHANNEL) if bot_config.MODLOGS_CHANNEL is not None else None
        self.leave_join_logs_channel = self.get_channel(id=bot_config.LEAVE_JOIN_LOGS_CHANNEL) if bot_config.LEAVE_JOIN_LOGS_CHANNEL is not None else None
        self.youtube_notifications_channel = self.get_channel(id=bot_config.YOUTUBE_NOTIFICATION_CHANNEL) if bot_config.YOUTUBE_NOTIFICATION_CHANNEL is not None else None
        self.reddit_notifications_channel = self.get_channel(id=bot_config.REDDIT_NOTIFICATION_CHANNEL) if bot_config.REDDIT_NOTIFICATION_CHANNEL is not None else None
        self.welcomes_channel = self.get_channel(id=bot_config.WELCOMES_CHANNEL) if bot_config.WELCOMES_CHANNEL is not None else None
        self.delete_logs_channel = self.get_channel(id=bot_config.DELETE_LOGS_CHANNEL) if bot_config.DELETE_LOGS_CHANNEL is not None else None
        self.edit_logs_channel = self.get_channel(bot_config.EDIT_LOGS_CHANNEL) if bot_config.EDIT_LOGS_CHANNEL is not None else None
        self.xp_multiplier = bot_config.XP_MULTIPLIER
        self.start_time = datetime.datetime.utcnow()
        self.db = None
        # self.clean_text = commands.clean_content(escape_markdown=True, fix_channel_mentions=True)
        dotenv.load_dotenv('.env')

    async def process_commands(self, message: discord.Message):
        if message.author.bot:
            return
        ctx = await self.get_context(message=message)
        await self.invoke(ctx)        

    async def on_connect(self):
        """Connect DB before bot is ready to assure that no calls are made before its ready"""

        self.db = await DataBase.create_pool(bot=self, uri=os.environ.get('POSTGRES_URI'), loop=self.loop)
        
        queries = ";".join([i[1] for i in inspect.getmembers(init_db) if not i[0].startswith("__")])
        await self.db.execute(queries)

    async def on_ready(self):
        for ext in cogs:
            try:
                self.load_extension(ext)
            except ExtensionAlreadyLoaded:
                pass
            except Exception as e:
                print(f"Error while loading {ext}", e)
        print(f'Successfully logged in as {self.user}\nConncted to {len(self.guilds)} guilds')

    async def on_member_join(self, member):
        responses = ['Welcome {}, we hope you brought pizza for us. \U0001F355']

        query = "INSERT INTO join_leave_logs(guild_id, member_id, action) VALUES($1, $2, $3)"

        await self.db.execute(query, member.guild.id, member.id, "join")

        if self.leave_join_logs_channel is not None:
            embed = discord.Embed(colour=discord.Colour.dark_blue())
            embed.add_field(name="Member", value=f"{member.mention}")
            embed.add_field(name="Member ID", value=f"{member.id}")
            embed.add_field(name="Action", value="Join")
            embed.add_field(name="Timestamp", value=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            embed.set_thumbnail(url=member.avatar_url)
            try:
                await self.leave_join_logs_channel.send(embed=embed)
            except Exception as e:
                print(e)

        if self.welcomes_channel is not None:
            try:
                await self.welcomes_channel.send(random.choice(responses).format(member.mention))
            except:
                pass

    async def on_member_remove(self, member):
        query = "INSERT INTO join_leave_logs(guild_id, member_id, action) VALUES($1, $2, $3)"

        await self.db.execute(query, member.guild.id, member.id, "leave")

        if self.leave_join_logs_channel is not None:
            embed = discord.Embed(colour=discord.Colour.dark_blue())
            embed.add_field(name="Member Name", value=f"{member.name}")
            embed.add_field(name="Member ID", value=f"{member.id}")
            embed.add_field(name="Action", value="Leave")
            embed.add_field(name="Timestamp", value=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            embed.set_thumbnail(url=member.avatar_url)
            try:
                await self.leave_join_logs_channel.send(embed=embed)
            except:
                pass

    async def on_message(self, message):
        if not message.guild:
            return
        await self.wait_until_ready()
        await Message.on_message(bot=self, message=message, xp_multiplier=self.xp_multiplier)
        return await self.process_commands(message)

    async def on_message_delete(self, message):
        if message.embeds or message.author.bot: return
        if self.delete_logs_channel is not None:
            embed = discord.Embed(description=f"Message deleted by {message.author.mention} in {message.channel.mention}",
                                  color=discord.Color.dark_orange())
            embed.add_field(name='Content', value=message.content)
            try:
                await self.delete_logs_channel.send(embed=embed)
            except:
                pass
        else:
            return

    async def on_message_edit(self, message_before: discord.Message , message_after: discord.Message):
        if message_before.embeds or message_after.embeds: return
        if message_before.author.bot or message_after.author.bot: return

        await Message.on_message(bot=self,message=message_after)
        if self.edit_logs_channel is not None:
            embed = discord.Embed(
                description=f"Message edited by {message_before.author.mention} in {message_before.channel.mention}",
                color=discord.Color.gold())
            embed.add_field(name='Original Message', value=f'{message_before.content}')
            embed.add_field(name='Edited Message', value=f'{message_after.content}\n[Go to message]({message_after.jump_url})')
            try:
                await self.edit_logs_channel.send(embed=embed)
            except:
                pass
        else:
            return

    async def on_command_error(self, ctx, error):
        print(error)
        message = None

        if hasattr(ctx.command, 'on_error'):
            return

        elif isinstance(error, BotMissingPermissions):
            message = await ctx.send(f'The bot is missing these permissions to do this command:\n{error.missing_perms}')

        elif isinstance(error, MissingPermissions):
            message = await ctx.send(f'You are missing these permissions to do this command.')

        elif isinstance(error, (BadUnionArgument, CommandOnCooldown, PrivateMessageOnly,
                                NoPrivateMessage, MissingRequiredArgument, ConversionError)):
            message = await ctx.send(str(error))

        elif isinstance(error, (BotMissingAnyRole, BotMissingRole)):
            message = await ctx.send(
                f'I am missing these roles to do this command: \n{error.missing_roles or [error.missing_role]}')

        elif isinstance(error, (MissingRole, MissingAnyRole)):
            message = await ctx.send(
                f'I am missing these roles to do this command: \n{error.missing_roles or [error.missing_role]}')

        elif isinstance(error, CommandNotFound):
            message = await ctx.send(str(error))

        elif isinstance(error, MemberNotFound):
            message = await ctx.send(str(error))
            
        elif isinstance(error, CheckFailure):
            message = await ctx.send(f'You are missing these permissions to do this command.')

        elif message is None:
            return await self.handle_error(ctx, error)

        await ctx.message.delete(delay=20.0)
        return await message.delete(delay=20.0)
    
    async def handle_error(self, ctx, error) -> None:
        error_channel = self.get_channel(int(os.environ.get("ERROR_CHANNEL")))
        trace = traceback.format_exception(
            type(error),
            error,
            error.__traceback__
        )
        paginator = commands.Paginator(prefix="", suffix="")

        for line in trace:
            paginator.add_line(line)

        def embed_exception(text: str, *, index: int = 0) -> discord.Embed:
            embed = discord.Embed(
                color=discord.Color(value=15532032),
                description=f"Command that caused the error: {ctx.message.content} from {ctx.author.name}\nError: {error}'"+ "```py\n%s\n```" % text,
                timestamp=datetime.datetime.utcnow(),
            )

            if not index:
                embed.title = "Error"

            return embed

        for page in paginator.pages:
            await error_channel.send(embed=embed_exception(page))

        return await ctx.send(embed=await failure_embed("Some error occred.", "The developer has been informed and should fix it soon."))


    @classmethod
    async def setup(cls, **kwargs):
        bot = cls()
        try:
            await bot.start(os.getenv('TOKEN'), **kwargs)
        except KeyboardInterrupt:
            await bot.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MartinGarrixBot.setup())
