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

from cogs.utils.DataBase.client import DataBase
from cogs.utils.DataBase.message import Message
from cogs.utils.DataBase import init_db
from cogs.utils.DataBase.guild_configuration import GuildConfig, Guild
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
        print(f'Successfully logged in as {self.user}\nConncted to {len(self.guilds)} guilds')


    async def on_guild_join(self, guild: discord.Guild):
        await GuildConfig.init_guild(bot=self, guild_id=guild.id)
        await Guild.init_guild(bot=self, guild_id=guild.id, name=guild.name, owner_id=guild.owner.id)
        intro_channel = None
        try:
            for channel in guild.text_channels:
                for name in ['chat', 'general', 'talk']:
                    if name in channel.name:
                        intro_channel = channel
                        raise Exception("Channel found")
        except Exception:
            pass

        milind = guild.get_member(421608483629301772)
        if milind is None:
            milind = "Milind Madhukar"
        else:
            milind = milind.mention
        embed = discord.Embed(title=f"{self.user.name}! +×",
                              description=f"I am a bot created by {milind}. I am a general purpose bot specifically targeted to be used by Garrixers. \n My prefixes are: {' ,'.join(['`' + i + '`' for i in self.command_prefix])}\nTo try me type `mg.help` to list all my commands.\nI might not be set up perfectly for your server.\n If you are an admin run `mg.help config` to configure me.",
                              colour=discord.Color.green())
        embed.set_image(url=self.user.avatar_url)
        if intro_channel is None:
            intro_channel = guild.text_channels[0]
        warning_embed = discord.Embed(title="Work in progress!", description="Please note that the bot is still a work in progress and the beta version of the bot is live right now. A lot of features are planned to be added relatively soon", colour=discord.Colour.gold())
        dm_me = f"feel free to DM {milind} with your concern." # Change this to the contact form instead.

        warning_embed.add_field(name="Support", value=f"If you find any bugs or want a feature to be added, {dm_me}\n")
        warning_embed.add_field(name="Upcoming Features!", value="A currency system called as garrix coins\nYoutube streaming in voice channels\nA better help command.\nAutomod for handling server raids\nJust to name a few")

        await intro_channel.send(embed=embed)
        return await intro_channel.send(embed=warning_embed)


    async def on_member_join(self, member):
        query = "SELECT * FROM timed_events WHERE user_id = $1 AND guild_id = $2 AND event_type = 'mute'"
        guild = member.guild
        timed_events = await self.db.fetch(query, member.id, guild.id)
        if timed_events:
            guild_config = await self.db.get_guild_config(guild_id=guild.id)
            muted_role = (guild.get_role(guild_config.muted_role)) or (discord.utils.get(guild.roles,name="Muted"))
            if muted_role is not None:
                await member.add_roles(muted_role, reason="Possible mute evasion.")
        responses = ['Welcome {}, we hope you brought pizza for us. \U0001F355']
        guild = await self.db.get_guild_config(guild_id=member.guild.id)

        welcomes_channel = self.get_channel(guild.welcomes_channel)
        leave_join_logs_channel = self.get_channel(guild.leave_join_logs_channel)

        query = """INSERT INTO join_leave_logs(guild_id, member_id, action)
                   VALUES($1, $2, $3)"""

        await self.db.execute(query, guild.guild_id, member.id, "join")

        if leave_join_logs_channel is not None:
            embed = discord.Embed(colour=discord.Colour.dark_blue())
            embed.add_field(name="Member", value=f"{member.mention}")
            embed.add_field(name="Member ID", value=f"{member.id}")
            embed.add_field(name="Action", value="Join")
            embed.add_field(name="Timestamp", value=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            embed.set_thumbnail(url=member.avatar_url)
            try:
                await leave_join_logs_channel.send(embed=embed)
            except Exception as e:
                print(e)

        if welcomes_channel is not None:
            try:
                await welcomes_channel.send(random.choice(responses).format(member.mention))
            except:
                pass

    async def on_member_remove(self, member):
        try:
            guild = await self.db.get_guild_config(guild_id=member.guild.id)
            leave_join_logs_channel = self.get_channel(guild.leave_join_logs_channel)
        except:
            return

        query = """INSERT INTO join_leave_logs(guild_id, member_id, action)
                           VALUES($1, $2, $3)"""

        await self.db.execute(query, guild.guild_id, member.id, "leave")

        if leave_join_logs_channel is not None:
            embed = discord.Embed(colour=discord.Colour.dark_blue())
            embed.add_field(name="Member Name", value=f"{member.name}")
            embed.add_field(name="Member ID", value=f"{member.id}")
            embed.add_field(name="Action", value="Leave")
            embed.add_field(name="Timestamp", value=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            embed.set_thumbnail(url=member.avatar_url)
            try:
                await leave_join_logs_channel.send(embed=embed)
            except:
                pass

    async def on_message(self, message):
        if not message.guild:
            return
        await self.wait_until_ready()
        await Message.on_message(bot=self, message=message)
        return await self.process_commands(message)

    async def on_guild_channel_delete(self, channel):
        try:
            await GuildConfig.on_guild_channel_delete(bot=self, channel=channel)
        except:
            pass

    async def on_guild_role_delete(self, role):
        try:
            await GuildConfig.on_guild_role_delete(bot=self, role=role)
        except:
            pass

    async def on_message_delete(self, message):
        if message.embeds or message.author.bot: return
        guild = await self.db.get_guild_config(guild_id=message.guild.id)
        delete_logs_channel = self.get_channel(guild.delete_logs_channel)
        if delete_logs_channel is not None:
            embed = discord.Embed(description=f"Message deleted by {message.author.mention} in {message.channel.mention}",
                                  color=discord.Color.dark_orange())
            embed.add_field(name='Content', value=message.content)
            try:
                await delete_logs_channel.send(embed=embed)
            except:
                pass
        else:
            return

    async def on_message_edit(self, message_before: discord.Message , message_after: discord.Message):
        if message_before.embeds or message_after.embeds: return
        if message_before.author.bot or message_after.author.bot: return

        await Message.on_message(bot=self,message=message_after)
        guild = await self.db.get_guild_config(guild_id=message_after.guild.id)
        edit_logs_channel = self.get_channel(guild.edit_logs_channel)
        if edit_logs_channel is not None:
            embed = discord.Embed(
                description=f"Message edited by {message_before.author.mention} in {message_before.channel.mention}",
                color=discord.Color.gold())
            embed.add_field(name='Original Message', value=f'{message_before.content}')
            embed.add_field(name='Edited Message', value=f'{message_after.content}\n[Go to message]({message_after.jump_url})')
            try:
                await edit_logs_channel.send(embed=embed)
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
