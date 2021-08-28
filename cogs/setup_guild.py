import discord
from discord.ext import commands
from discord.ext.commands.errors import *

from .utils.custom_embed import success_embed, failure_embed


class GuildSetup(commands.Cog, name="Configure"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        """Config Command to show all possible settings for your server."""

        guild = await self.bot.db.get_guild_config(ctx.guild.id)
        if guild is None:
            await ctx.message.delete(delay=10.0)
            message = await ctx.send('Could not register your guild. Try kicking the bot and re-inviting it back to fix the issue.')
            return await message.delete(delay=10.0)
        embed = discord.Embed(title=f"{ctx.guild.name} Configuration",
                              description="To set a value use any of the following commands.\nNone of the attributes are compulsary but for all the features to work, you can set all the attributes.",
                              colour=discord.Color.blue())
        muted_role = discord.utils.get(ctx.guild.roles, id=guild.muted_role)
        embed.add_field(name="Muted Role",
                        value=f"A role when given to a member, cannot talk in the server when muted by a moderator.\nCurrent Value: {muted_role.mention if guild.muted_role and muted_role is not None else 'Not Set.'} \nCommand: `mg.config muted`",
                        inline=False)
        modlogs_channel = discord.utils.get(ctx.guild.text_channels, id=guild.modlogs_channel)
        embed.add_field(name="Modlogs Channel",
                        value=f"A channel where all the modlogs are stored. These include warn, mute, kick and ban\nCurrent Value: {modlogs_channel.mention if guild.modlogs_channel and modlogs_channel is not None else 'Not Set.'} \nCommand: `mg.config modlogs`",
                        inline=False)
        leave_join_channel = discord.utils.get(ctx.guild.text_channels, id=guild.leave_join_logs_channel)
        embed.add_field(name="Leave Join Logs Channel",
                        value=f"A channel where all the member leave join activity is logged.\nCurrent Value: {leave_join_channel.mention if guild.leave_join_logs_channel and leave_join_channel is not None else 'Not Set.'} \nCommand: `mg.config leave_join`",
                        inline=False)
        youtube_notification_channel = discord.utils.get(ctx.guild.text_channels, id=guild.youtube_notifications_channel)
        embed.add_field(name="Youtube Notifications Channel",
                        value=f"A channel where all Martin Garrix youtube notifications are sent.\nCurrent Value: {youtube_notification_channel.mention if guild.youtube_notifications_channel and youtube_notification_channel is not None else 'Not Set.'} \nCommand: `mg.config youtube`",
                        inline=False)
        reddit_notification_channel = discord.utils.get(ctx.guild.text_channels, id=guild.reddit_notifications_channel)
        embed.add_field(name="Reddit Notifications Channel",
                        value=f"A channel where all Martin Garrix subreddit (r/Martingarrix) notifications are sent.\nCurrent Value: {reddit_notification_channel.mention if guild.reddit_notifications_channel and reddit_notification_channel is not None else 'Not Set.'} \nCommand: `mg.config reddit`",
                        inline=False)
        welcomes_channel = discord.utils.get(ctx.guild.text_channels, id=guild.welcomes_channel)
        embed.add_field(name="Welcomes Channel",
                        value=f"A channel where all new members of your server are shown.\nCurrent Value: {welcomes_channel.mention if guild.welcomes_channel and welcomes_channel is not None else 'Not Set.'} \nCommand: `mg.config welcomes`",
                        inline=False)
        delete_logs_channel = discord.utils.get(ctx.guild.text_channels, id=guild.delete_logs_channel)
        embed.add_field(name="Delete Logs Channel",
                        value=f"A channel where all the deleted messages are shown.\nCurrent Value: {delete_logs_channel.mention if guild.delete_logs_channel and delete_logs_channel is not None else 'Not Set.'} \nCommand: `mg.config deletes`",
                        inline=False)
        edit_logs_channel = discord.utils.get(ctx.guild.text_channels, id=guild.edit_logs_channel)
        embed.add_field(name="Edit Logs Channel",
                        value=f"A channel where all the edited messages are shown.\nCurrent Value: {edit_logs_channel.mention if guild.edit_logs_channel and edit_logs_channel is not None else 'Not Set.'} \nCommand: `mg.config edits`",
                        inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="XP Multiplier",
                        value=f"Multiplier for the XP for levelling.\nCurrent Value: {guild.xp_multiplier} \nCommand: `mg.config multiplier`",
                        inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @config.command()
    @commands.has_permissions(administrator=True)
    async def muted(self, ctx, muted_role: discord.Role = None):
        if muted_role is None:
            embed = discord.Embed(title="Update muted role",
                                  description="To update the role, type `mg.config muted <Mention role or role id>`",
                                  colour=discord.Color.dark_teal())
            return await ctx.send(embed=embed)
        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        if muted_role in ctx.guild.roles:
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=True)
            await guild.update_muted_role(muted_role=muted_role.id)
            embed = await success_embed(f"Muted Role updated successfully to {muted_role.name}")
            await ctx.send(embed=embed)
        else:
            embed = await success_embed(title="Could not update muted role", description="Role does not exist.")
            return await ctx.send(embed=embed)

    @muted.error
    async def muted_error(self, ctx, error):
        embed = None
        if isinstance(error, RoleNotFound):
            embed = await failure_embed("Could not update muted role.", description="Role was not found.")
        elif isinstance(error, MissingPermissions):
            embed =await failure_embed("You don't have the permissions to do that.")
        else:
            embed = await failure_embed("Could not update muted role.", description="Some error occurred.")
            print(error)
        return await ctx.send(embed=embed)

    @config.command()
    @commands.has_permissions(administrator=True)
    async def modlogs(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            embed = discord.Embed(title="Update modlogs channel",
                                  description="To update the channel, type `mg.config modlogs <Mention channel or channel id>`",
                                  colour=discord.Color.dark_teal())
            return await ctx.send(embed=embed)
        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        if channel in ctx.guild.text_channels:
            await guild.update_modlogs_channel(modlogs_channel=channel.id)
            embed = await success_embed(f"Modlogs channel updated successfully to {channel.name}")
            return await ctx.send(embed=embed)

    @modlogs.error
    async def modlogs_error(self, ctx, error):
        embed = None
        if isinstance(error, ChannelNotFound):
            embed = await failure_embed("Could not update modlogs channel.", description="Channel was not found.")
        elif isinstance(error, MissingPermissions):
            embed = await failure_embed("You don't have the permissions to do that.")
        else:
            embed = await failure_embed("Could not update modlogs channel.", description="Some error occurred.")
            print(error)
        return await ctx.send(embed=embed)

    @config.command()
    @commands.has_permissions(administrator=True)
    async def leave_join(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            embed = discord.Embed(title="Update leave join logs channel",
                                  description="To update the channel, type `mg.config leave_join <Mention channel or channel id>`",
                                  colour=discord.Color.dark_teal())
            return await ctx.send(embed=embed)
        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        if channel in ctx.guild.text_channels:
            await guild.update_leave_join_logs_channel(leave_join_logs_channel=channel.id)
            embed = await success_embed(f"Leave join logs channel updated successfully to {channel.name}")
            return await ctx.send(embed=embed)

    @leave_join.error
    async def leave_join_error(self, ctx, error):
        embed = None
        if isinstance(error, ChannelNotFound):
            embed = await failure_embed("Could not update leave join logs channel.",
                                        description="Channel was not found.")
        elif isinstance(error, MissingPermissions):
            embed =await failure_embed("You don't have the permissions to do that.")
        else:
            embed = await failure_embed("Could not update leave join logs channel.", description="Some error occurred.")
            print(error)
        return await ctx.send(embed=embed)

    @config.command()
    @commands.has_permissions(administrator=True)
    async def youtube(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            embed = discord.Embed(title="Update youtube notifications channel",
                                  description="To update the channel, type `mg.config youtube <Mention channel or channel id>`",
                                  colour=discord.Color.dark_teal())
            return await ctx.send(embed=embed)
        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        if channel in ctx.guild.text_channels:
            await guild.update_youtube_notifications_channel(youtube_notifications_channel=channel.id)
            embed = await success_embed(f"Youtube Notifications channel updated successfully to {channel.name}")
            return await ctx.send(embed=embed)

    @youtube.error
    async def youtube_error(self, ctx, error):
        embed = None
        if isinstance(error, ChannelNotFound):
            embed = await failure_embed("Could not update youtube notifications channel.",
                                        description="Channel was not found.")
        elif isinstance(error, MissingPermissions):
            embed =await failure_embed("You don't have the permissions to do that.")
        else:
            embed = await failure_embed("Could not update youtube notifications channel.",
                                        description="Some error occurred.")
            print(error)
        return await ctx.send(embed=embed)

    @config.command()
    @commands.has_permissions(administrator=True)
    async def reddit(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            embed = discord.Embed(title="Update reddit notifications channel",
                                  description="To update the channel, type `mg.config reddit <Mention channel or channel id>`",
                                  colour=discord.Color.dark_teal())
            return await ctx.send(embed=embed)
        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        if channel in ctx.guild.text_channels:
            await guild.update_reddit_notifications_channel(reddit_notifications_channel=channel.id)
            embed = await success_embed(f"Reddit Notifications channel updated successfully to {channel.name}")
            return await ctx.send(embed=embed)

    @reddit.error
    async def reddit_error(self, ctx, error):
        if isinstance(error, ChannelNotFound):
            embed = await failure_embed("Could not update reddit notifications channel.",
                                        description="Channel was not found.")
        elif isinstance(error, MissingPermissions):
            embed =await failure_embed("You don't have the permissions to do that.")
        else:
            embed = await failure_embed("Could not update reddit notifications channel.",
                                        description="Some error occurred.")
            print(error)
        return await ctx.send(embed=embed)

    @config.command()
    @commands.has_permissions(administrator=True)
    async def welcomes(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            embed = discord.Embed(title="Update welcomes channel",
                                  description="To update the channel, type `mg.config welcomes <Mention channel or channel id>`",
                                  colour=discord.Color.dark_teal())
            return await ctx.send(embed=embed)

        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        if channel in ctx.guild.text_channels:
            await guild.update_welcomes_channel(welcomes_channel=channel.id)
            embed = await success_embed(f"Welcomes channel updated successfully to {channel.name}")
            return await ctx.send(embed=embed)


    @welcomes.error
    async def welcomes_error(self, ctx, error):
        embed = None
        if isinstance(error, ChannelNotFound):
            embed = await failure_embed("Could not update welcomes channepl.",
                                        description="Channel was not found.")
        elif isinstance(error, MissingPermissions):
            embed =await failure_embed("You don't have the permissions to do that.")
        else:
            embed = await failure_embed("Could not update welcomes channel.",
                                        description="Some error occurred.")
            print(error)
        return await ctx.send(embed=embed)

    @config.command()
    @commands.has_permissions(administrator=True)
    async def deletes(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            embed = discord.Embed(title="Update Delete Logs Channel",
                                  description="To update the channel, type `mg.config deletes <Mention channel or channel id>`",
                                  colour=discord.Color.dark_teal())
            return await ctx.send(embed=embed)

        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        if channel in ctx.guild.text_channels:
            await guild.update_delete_logs_channel(delete_logs_channel=channel.id)
            embed = await success_embed(f"Delete Logs channel updated successfully to {channel.name}")
            return await ctx.send(embed=embed)

    @deletes.error
    async def deletes_error(self, ctx, error):
        embed = None
        if isinstance(error, ChannelNotFound):
            embed = await failure_embed("Could not update delete logs channel.",
                                        description="Channel was not found.")
        elif isinstance(error, MissingPermissions):
            embed = await failure_embed("You don't have the permissions to do that.")
        else:
            embed = await failure_embed("Could not update delete logs channel.",
                                        description="Some error occurred.")
            print(error)
        return await ctx.send(embed=embed)

    @config.command()
    @commands.has_permissions(administrator=True)
    async def edits(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            embed = discord.Embed(title="Update Edit Logs Channel",
                                  description="To update the channel, type `mg.config edits <Mention channel or channel id>`",
                                  colour=discord.Color.dark_teal())
            return await ctx.send(embed=embed)

        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        if channel in ctx.guild.text_channels:
            await guild.update_edit_logs_channel(edit_logs_channel=channel.id)
            embed = await success_embed(f"Edit Logs channel updated successfully to {channel.name}")
            return await ctx.send(embed=embed)

    @edits.error
    async def edits_error(self, ctx, error):
        embed = None
        if isinstance(error, ChannelNotFound):
            embed = await failure_embed("Could not update edits logs channel.",
                                        description="Channel was not found.")
        elif isinstance(error, MissingPermissions):
            embed = await failure_embed("You don't have the permissions to do that.")
        else:
            embed = await failure_embed("Could not update edits logs channel.",
                                        description="Some error occurred.")
            print(error)
        return await ctx.send(embed=embed)

    @config.command()
    @commands.has_permissions(administrator=True)
    async def multiplier(self, ctx, value: int = None):
        if value is None:
            embed = discord.Embed(title="Update XP multiplier",
                                  description="To update the XP Multiplier, type `mg.config multiplier <Multiplier value>",
                                  colour=discord.Color.dark_teal())
            return await ctx.send(embed=embed)

        guild = await self.bot.db.get_guild_config(guild_id=ctx.guild.id)
        await guild.update_xp_multiplier(xp_multiplier=value)
        embed = await success_embed(f"XP Multiplier updated successfully to {value}")
        return await ctx.send(embed=embed)

    @multiplier.error
    async def multiplier_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            embed = await failure_embed("You don't have the permissions to do that.")
        else:
            embed = await failure_embed("Could not update the XP multiplier.",
                                        description="Some error occurred.")
            print(error)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildSetup(bot=bot))
