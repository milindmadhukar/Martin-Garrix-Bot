import discord
from discord.ext import commands
from datetime import datetime,timezone
import typing
import asyncio

query = """INSERT INTO modlogs(user_id, moderator_id, guild_id, log_type, reason) VALUES ($1, $2, $3, $4, $5)"""

class Moderation(commands.Cog):
    def __init__(self, bot) :
        self.bot = bot
        # self.check_timed_events.start()

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
        if self.bot.modlogs_channel is None:
            return
        modlogs_embed = discord.Embed(title=f"Member Kicked!",color = discord.Color.red())
        modlogs_embed.add_field(name="Member Kicked", value=f'{member.mention}',inline=False)
        modlogs_embed.add_field(name="Member ID", value=f'{member.id}',inline=False)
        modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
        modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
        modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)
        return await self.bot.modlogs_channel.send(embed=modlogs_embed)

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
        if self.bot.modlogs_channel is None:
            return
        modlogs_embed = discord.Embed(title=f"Member Banned!",color = discord.Color.red())
        modlogs_embed.add_field(name="Member Banned", value=f'{member.mention}',inline=False)
        modlogs_embed.add_field(name="Member ID", value=f'{member.id}',inline=False)
        modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
        modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
        modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)
        return await self.bot.modlogs_channel.send(embed=modlogs_embed)

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
            if self.bot.modlogs_channel is None:
                return
            modlogs_embed = discord.Embed(title=f"Member Unbanned!",color = discord.Color.green())
            modlogs_embed.add_field(name="Member Unbanned", value=f'{user.mention}',inline=False)
            modlogs_embed.add_field(name="Member ID", value=f'{user.id}',inline=False)
            modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
            modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
            modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)
            await self.bot.modlogs_channel.send(embed=modlogs_embed)


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
        if self.bot.modlogs_channel is None:
            return
        modlogs_embed = discord.Embed(title=f"Member Warned!",color = discord.Color.red())
        modlogs_embed.add_field(name="Member Warned", value=f'{member.mention}',inline=False)
        modlogs_embed.add_field(name="Member ID", value=f'{member.id}',inline=False)
        modlogs_embed.add_field(name="Reason", value=f'{reason}',inline=False)
        modlogs_embed.add_field(name="Moderator", value=f'{ctx.author.mention}',inline=False)
        modlogs_embed.add_field(name="Time in UTC", value=str(datetime.now(timezone.utc)).split('.')[0],inline=False)
        await self.bot.modlogs_channel.send(embed=modlogs_embed)

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


    # @tasks.loop(minutes=1)
    # async def check_timed_events(self):
    #     events_query = "SELECT * FROM timed_events WHERE EXTRACT (SECONDS  FROM (end_time - NOW())) < 0"
    #     records = await self.bot.db.fetch(events_query)
    #
    #     for record in records:
    #         if record['event_type'] == "mute":
    #             guild = self.bot.get_guild(id=record['guild_id'])
    #             member = guild.get_member(record['user_id'])
    #             if member is None or guild is None:
    #                 continue
    #             await asyncio.sleep(1)
    #             guild_config = await self.bot.db.get_guild_config(guild_id=record['guild_id'])
    #             muted_role = (guild.get_role(guild_config.muted_role)) or (discord.utils.get(guild.roles,name="Muted"))
    #             try:
    #                 await member.remove_roles(muted_role, reason="Muted duration expired.")
    #             except:
    #                 pass
    #             await self.bot.db.execute('DELETE FROM timed_events WHERE id = $1', record['id'])
    #             embed = discord.Embed(embed=await success_embed(f"You have been unmuted in {guild.name}", description="Mute duration lapsed."))
    #             try:
    #                 await member.send(embed=embed)
    #             except:
    #                 pass

def setup(bot):
    bot.add_cog(Moderation(bot))
