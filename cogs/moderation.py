import discord
from discord.ext import commands, tasks
from aiohttp import request
from datetime import datetime,timezone
from json import dumps
from asyncpg.exceptions import IntegrityConstraintViolationError
import os
import typing
import asyncio

from .utils.custom_embed import failure_embed, success_embed
from .utils.time import parse_time

query = """INSERT INTO modlogs(user_id, moderator_id, guild_id, log_type, reason) VALUES ($1, $2, $3, $4, $5)"""

class Moderation(commands.Cog):
    def __init__(self, bot) :
        self.bot = bot
        self.check_timed_events.start()

    @commands.command(help="Kick a member from the server")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member,*, reason="Not specified"):
        dm = ""
        moderator = ctx.author
        await ctx.message.delete()
        await self.bot.db.execute(query, member.id, moderator.id, ctx.guild.id, "kick", reason)
        action_embed = discord.Embed(title=f"You were kicked from the {ctx.guild.name} server.",colour= discord.Color.red())
        action_embed.add_field(name="Reason", value=reason, inline=False)
        try:
            await member.send(embed=action_embed)
        except:
            dm = "Could not DM member."
        await member.kick(reason=reason)
        embed = discord.Embed(title=f"<a:tick:810462879374770186> {member.display_name} has been kicked. {dm}", color = discord.Color.red())
        await ctx.send(embed=embed)
        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        modlogs_channel_id = guild.modlogs_channel
        if modlogs_channel_id is None:
            return
        modlogs_embed = discord.Embed(title=f"Member Kicked!",color = discord.Color.red())
        modlogs_embed.add_field(name="Member Kicked", value=f'{member.mention}',inline=False)
        modlogs_embed.add_field(name="Member ID", value=f'{member.id}',inline=False)
        modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
        modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
        modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)
        channel = ctx.guild.get_channel(modlogs_channel_id)
        return await channel.send(embed=modlogs_embed)

    @commands.command(help="Ban a member from the server")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason="Not specified"):
        dm = ""
        moderator = ctx.author
        await ctx.message.delete()
        await self.bot.db.execute(query, member.id, moderator.id, ctx.guild.id, "ban", reason)
        action_embed = discord.Embed(title=f"You were banned from the {ctx.guild.name} server.",colour= discord.Color.red())
        action_embed.add_field(name="Reason", value=reason, inline=False)
        try:
            await member.send(embed=action_embed)
        except:
            dm = "Could not DM member."
        await member.ban(reason=reason)
        embed = discord.Embed(title=f"<a:tick:810462879374770186> {member.display_name} has been banned. {dm}", color = discord.Color.red())
        await ctx.send(embed=embed)
        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        modlogs_channel_id = guild.modlogs_channel
        if modlogs_channel_id is None:
            return
        modlogs_embed = discord.Embed(title=f"Member Banned!",color = discord.Color.red())
        modlogs_embed.add_field(name="Member Banned", value=f'{member.mention}',inline=False)
        modlogs_embed.add_field(name="Member ID", value=f'{member.id}',inline=False)
        modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
        modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
        modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)
        channel = self.bot.get_channel(modlogs_channel_id)
        return await channel.send(embed=modlogs_embed)

    @commands.command(help="Unban a member from the server")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member:str, *, reason = "Not specified"):
        moderator = ctx.author
        member_name = None
        discriminator = None
        banned_users = await ctx.guild.bans()
        if '#' in member:
            member_name,discriminator = member.split('#')

        elif member.isdigit():
            unban_member = self.bot.get_user(int(member))
            member_name,discriminator = unban_member.name, unban_member.discriminator

        else:
            ctx.send('Member was not found')
            return

        for ban_entry in banned_users:
            user = ban_entry.user
            await ctx.message.delete()
            if user.name != member_name or user.disciminator != discriminator:
                continue
            await ctx.guild.unban(user)
            embed = discord.Embed(title=f"<a:tick:810462879374770186> {user.display_name} has been unbanned. {dm}", color = discord.Color.green())
            await self.bot.db.execute(query, user.id, moderator.id, ctx.guild.id, "unban", reason)
            await ctx.send(embed=embed)
            guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
            modlogs_channel_id = guild.modlogs_channel
            if modlogs_channel_id is None:
                return
            modlogs_embed = discord.Embed(title=f"Member Unbanned!",color = discord.Color.green())
            modlogs_embed.add_field(name="Member Unbanned", value=f'{user.mention}',inline=False)
            modlogs_embed.add_field(name="Member ID", value=f'{user.id}',inline=False)
            modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
            modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
            modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)
            channel = self.bot.get_channel(modlogs_channel_id)
            await channel.send(embed=modlogs_embed)


    @commands.command(help="Warn a member with a specified reason")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member : discord.Member, *, reason):
        dm = ""
        moderator = ctx.author
        await ctx.message.delete()
        await self.bot.db.execute(query, member.id, moderator.id, ctx.guild.id, "warn", reason)
        action_embed = discord.Embed(title=f"You have been warned in the {ctx.guild.name} server.",colour= discord.Color.red())
        action_embed.add_field(name="Reason", value=reason, inline=False)
        try:
            await member.send(embed=action_embed)
        except:
            dm = "Could not DM member."
        embed = discord.Embed(title=f"<a:tick:810462879374770186> {member.display_name} was warned. {dm}", color = discord.Color.red())
        await ctx.send(embed=embed)
        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        modlogs_channel_id = guild.modlogs_channel
        if modlogs_channel_id is None:
            return
        modlogs_embed = discord.Embed(title=f"Member Warned!",color = discord.Color.red())
        modlogs_embed.add_field(name="Member Warned", value=f'{member.mention}',inline=False)
        modlogs_embed.add_field(name="Member ID", value=f'{member.id}',inline=False)
        modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
        modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
        modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)
        channel = ctx.guild.get_channel(modlogs_channel_id)
        await channel.send(embed=modlogs_embed)

    @commands.command(help="Mass delete specified amount of messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount= 5):
        await ctx.channel.purge(limit=amount+1)
        embed = discord.Embed(title=f"<a:tick:810462879374770186> Purged {amount} Messages!", color = discord.Color.green())
        message = await ctx.send(embed=embed)
        return await message.delete(delay=10)

    @commands.command(help="Show modlogs of a member")
    @commands.has_permissions(view_audit_log=True)
    async def modlogs(self, ctx, member: typing.Union[discord.Member, discord.User]):
        modlogs = await self.bot.db.fetch("SELECT * FROM modlogs WHERE user_id = $1 AND guild_id = $2", member.id, ctx.guild.id) 
        if not modlogs:
            message = await ctx.send("No modlogs found for this user")
            return await message.delete(delay=60.0)
        pager = commands.Paginator(prefix="", suffix="")
        for modlog in modlogs:
            pager.add_line(line=f"```Case #{modlog['id']}\nType: {modlog['log_type']}\nReason: {modlog['reason']}\nModerator: {ctx.guild.get_member(modlog['moderator_id']).display_name}\nDate: {modlog['time'].strftime('%b %d %Y, %H:%M:%S')}\n\n```")
            
        await ctx.send(f'A total of {len(modlogs)} modlog(s) found for this user.')

        def embed_exception(text: str, *, index: int = 0) -> discord.Embed:
            embed = discord.Embed(
                color=discord.Color.red(),
                description=text,
                timestamp=datetime.utcnow(),
            )

            if not index:
                embed.title = f"Modlogs for {member.display_name}"

            return embed

        for page in pager.pages:
            await ctx.send(embed=embed_exception(page), delete_after=600)
            await asyncio.sleep(1)



    @commands.command(help="Restrict a member from sending messages.")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member : discord.Member, duration:str = None, *, reason="Not specified"):
        moderator = ctx.author
        guild = ctx.guild
        
        await ctx.message.delete()

        guild_config = await self.bot.db.get_guild_config(guild_id=guild.id)
        muted_role = (guild.get_role(guild_config.muted_role)) or (discord.utils.get(guild.roles,name="Muted"))   

        if muted_role is None:
            await ctx.send("A 'Muted' role does not exist. Do you want me to create it?")
            check = lambda m: (m.author.id == ctx.author.id and m.channel.id == ctx.channel.id)
            try:
                createRole = await self.bot.wait_for('message', check=check, timeout = 180)
                if createRole.content.lower() in ['yes', 'y', 'ye', 'okay', 'ok' , 'k']:
                    role = await guild.create_role(name="Muted")
                    await role.edit(colour=discord.Colour(0x191919))
                    # Set position
                    await ctx.invoke(self.bot.get_command('config muted'), muted_role = role)
                else:
                    return await ctx.send(embed=await failure_embed("Couldn't mute member.", description="Please create a muted role."))
            except asyncio.TimeoutError:
                return await ctx.send(embed = await failure_embed("Response timed out."))

        print("I am here hopefully")

        if duration is not None:
            time = parse_time(duration)
            if time is None:
                return await ctx.send(embed = await failure_embed("Please enter a valid duration for mute."))
            else:
                timed_event = "INSERT INTO timed_events(event_type, user_id, guild_id, end_time) VALUES ($1, $2, $3, $4)"
                try:
                    await self.bot.db.execute(timed_event, "mute", member.id, guild.id, datetime.now() + time)
                except IntegrityConstraintViolationError:
                    return await ctx.send(embed = await failure_embed(title="Could not mute member. The member may already be muted."))
        
        dm = ""


        print(member, moderator)

        await self.bot.db.execute(query, member.id, moderator.id, guild.id, "mute", reason)
        await member.add_roles(muted_role, reason=reason)

        dm_embed = discord.Embed(title=f"You were muted in the {guild.name} server for {time}")
        try:
            await member.send(embed=dm_embed)
        except:
            dm = "Could not DM member."

        embed = discord.Embed(title=f"{member} was muted for {time}. {dm}") # Format time to string
        await ctx.send(embed=embed)
       
        modlogs_channel_id = guild_config.modlogs_channel
        if modlogs_channel_id is None:
            return

        modlogs_embed = discord.Embed(title=f"<a:tick:810462879374770186> Member Muted!")
        modlogs_embed.add_field(name="Member Muted", value=f'{member.mention}',inline=False)
        modlogs_embed.add_field(name="Member ID", value=f'{member.id}',inline=False)
        modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
        modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
        modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)


        channel = self.bot.get_channel(modlogs_channel_id)
        await channel.send(embed=modlogs_embed)

    @commands.command(help="Unmute a member.")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member : discord.Member,*, reason="Not specified"):
        moderator = ctx.author
        guild = ctx.guild
        muted_role = discord.utils.get(guild.roles,name="Muted")

        async with request('PUT', f'{API_URL}/user/update', data={
            'token' : 'test',
            'user_id' : member.id,
            'modlogs' : dumps(['unmute', reason, moderator, str(datetime.now(timezone.utc)).split('.')[0]]),
            'remove_role' : dumps({'muted' : str(muted_role.id)})
        }) as response:
            print(response.status)
            if response.status == 200:
                await ctx.message.delete()
                await member.remove_roles(muted_role, reason=reason)
                embed = discord.Embed(title=f"<a:tick:810462879374770186> {member} was unmuted.", color = discord.Color.green()) #Change to black
                message = await ctx.send(embed=embed)
                dm_embed = discord.Embed(title=f"You were unmuted.\nReason: {reason}",color = discord.Color.green())
                try:
                    await member.send(embed=dm_embed)
                except:
                    pass
                modlogs_channel_id = int(os.environ.get('MODLOGS_CHANNEL'))
                print(modlogs_channel_id, type(modlogs_channel_id))
                modlogs_embed = discord.Embed(title=f"<a:tick:810462879374770186> Member Unmuted!",color = discord.Color.green())
                modlogs_embed.add_field(name="Member Unmuted", value=f'{member.mention}',inline=False)
                modlogs_embed.add_field(name="Member ID", value=f'{member.id}',inline=False)
                modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
                modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
                modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)
                channel = self.bot.get_channel(modlogs_channel_id)
                print(channel)
                await channel.send(embed=modlogs_embed)
                return await message.delete(delay=30.0)
            else:
                milind = self.bot.get_user(421608483629301772)
                dm = await milind.create_dm()
                await dm.send(f"Couldn't unmute member, check into this issue.\nUser Details:\nUsername: {member.name}#{member.discriminator}\nUser ID: {member.id}")

    @tasks.loop(minutes=1)
    async def check_timed_events(self):
        events_query = "SELECT * FROM timed_events WHERE EXTRACT (SECONDS  FROM (end_time - NOW())) < 0"
        records = await self.bot.db.fetch(events_query)

        for record in records:
            if record['event_type'] == "mute":
                guild = self.bot.get_guild(id=record['guild_id'])
                member = guild.get_member(record['user_id'])
                if member is None or guild is None:
                    continue
                await asyncio.sleep(1)
                guild_config = await self.bot.db.get_guild_config(guild_id=record['guild_id'])
                muted_role = (guild.get_role(guild_config.muted_role)) or (discord.utils.get(guild.roles,name="Muted"))
                try:
                    await member.remove_roles(muted_role, reason="Muted duration expired.")
                except:
                    pass
                await self.bot.db.execute('DELETE FROM timed_events WHERE id = $1', record['id'])
                embed = discord.Embed(embed=await success_embed(f"You have been unmuted in {guild.name}", description="Mute duration lapsed."))
                try:
                    await member.send(embed=embed)
                except:
                    pass

def setup(bot):
    bot.add_cog(Moderation(bot))
