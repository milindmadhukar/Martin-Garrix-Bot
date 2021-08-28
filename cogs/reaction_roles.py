import discord
from discord.ext import commands
import asyncio
import emojis as emoji_module
from discord.ext.commands.errors import BadArgument
from cogs.utils import custom_embed

class ReactionRoles(commands.Cog):
    def __init__(self, bot) :
        self.bot = bot
    
    @commands.has_permissions(administrator=True)
    @commands.command(help="Create a reaction role message by assigning roles to emojis.", aliases=['createReaction'])
    async def create_reaction_role(self, ctx):
        embed = discord.Embed(title="Create a reaction role.", description="Enter the channel to send message in.", colour=discord.Colour.gold())
        check = lambda m: (m.author.id == ctx.author.id and m.channel.id == ctx.channel.id)
        await ctx.send(embed=embed)
        guild = ctx.guild
        channel = None
        title = None
        emojis_role_data = []
        timeout_embed = await custom_embed.failure_embed("Setup time out. Please try again.")
        try:
            user_input = await self.bot.wait_for('message', check=check, timeout = 180)
            channel = await commands.TextChannelConverter().convert(ctx=ctx, argument=user_input.content)
            await ctx.send(f"Reaction role channel set to be: {channel.mention}")
        except BadArgument:
            return await ctx.send(embed= await custom_embed.failure_embed("Reaction role setup failed.", description="Please enter a valid channel."))
        except asyncio.TimeoutError:
            return await ctx.send(embed=timeout_embed)
        
        embed.title = None
        embed.description = "Enter the title/category of reaction role."

        await ctx.send(embed=embed)
        try:
            title = await self.bot.wait_for('message', check=check, timeout = 180)
            title = title.content
        except asyncio.TimeoutError:
            return await ctx.send(embed=timeout_embed)
        
        await ctx.send(f"Title set to be: {title}")

        user_input = None
        count = 0
        try:
            while user_input != 'exit' and count < 20:
                count += 1
                await ctx.send(f"""Enter Role name. {"Type 'exit' to stop adding roles." if count > 1 else ''}""")
                user_input = await self.bot.wait_for('message', check=check, timeout = 180)
                if user_input.content == 'exit':
                    break
                role = discord.utils.get(guild.roles, name=user_input.content)
                if role is None:
                    await ctx.send("That role does not exist. Do you want me to create it?")
                    createRole = await self.bot.wait_for('message', check=check, timeout = 180)
                    if createRole.content.lower() in ['yes', 'y', 'ye', 'okay', 'ok' , 'k']:
                        role = await guild.create_role(name=user_input.content)
                        await ctx.send(f"Created the role {role.mention} !")
                    else:
                        count -= 1
                        continue
                elif role.position > guild.get_member(self.bot.user.id).roles[-1].position:
                    await ctx.send("Missing permissions to add the role. That role is higher than my role. Place the role below my role to add it to reaction roles.")
                    count -= 1
                    continue
                embed.description = f"Enter the emoji corresponding to the role {role.mention}"
                await ctx.send(embed=embed)
                emoji = await self.bot.wait_for('message', check=check, timeout = 180)
                emoji = emoji.content
                if emoji_module.count(emoji) == 0:
                    try:
                        emoji = await commands.PartialEmojiConverter().convert(ctx=ctx, argument=emoji)
                    except BadArgument:
                        await ctx.send(embed=await custom_embed.failure_embed(title="Bad emoji argument. Please retry."))
                        count -= 1
                        role = None
                        continue

                emojis_role_data.append([role, str(emoji)])
            if len(emojis_role_data) == 0:
                return
            description = ""
            for data in emojis_role_data:
                description += f"{data[1]} for the {data[0].mention} role.\n"
            reaction_embed = discord.Embed(title=title, color=discord.Colour.blue())
            reaction_embed.add_field(name="The emojis and corresponding roles are:", value=description)
            reaction_message = await channel.send(embed=reaction_embed)
            await self.bot.db.execute("INSERT INTO reaction_roles (guild_id, message_id) VALUES ($1,$2)", reaction_message.guild.id, reaction_message.id)
            reaction_message_fk = await self.bot.db.fetchrow("SELECT id FROM reaction_roles WHERE guild_id = $1 AND message_id = $2", reaction_message.guild.id, reaction_message.id)
            query = "INSERT INTO emoji_role (emoji, role_id, reaction_role_id) VALUES ($1, $2, $3)"
            for data in emojis_role_data:
                try:
                    await self.bot.db.execute(query, str(data[1]), data[0].id, reaction_message_fk['id'])
                except:
                    pass
                await reaction_message.add_reaction(data[1])
                await asyncio.sleep(0.5)
            return await ctx.send(embed=await custom_embed.success_embed("Successfully created the reaction roles."))
        except asyncio.TimeoutError:
            return await ctx.send(embed=timeout_embed)



    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.member.bot:
            return
        query = "SELECT message_id FROM reaction_roles WHERE guild_id = $1"
        reaction_roles = await self.bot.db.fetch(query, payload.guild_id)
        if payload.message_id not in [role['message_id'] for role in reaction_roles]:
            return
        else:
            guild_id = payload.guild_id
            query = "SELECT * FROM reaction_roles JOIN emoji_role ON emoji_role.reaction_role_id = reaction_roles.id WHERE reaction_roles.guild_id = $1 AND reaction_roles.message_id = $2"
            records = await self.bot.db.fetch(query, guild_id, payload.message_id)
            role = None
            records = {record['emoji']: record['role_id'] for record in records}
            role_id = records.get(str(payload.emoji))
            if role_id is not None:
                guild = self.bot.get_guild(guild_id)
                role = guild.get_role(role_id)
            if role is not None:
                await payload.member.add_roles(role, reason="Reaction Role")
                try:
                    return await payload.member.send(f'Gave you the **{role.name}** role!')
                except:
                    pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        query = "SELECT message_id FROM reaction_roles WHERE guild_id = $1"
        reaction_roles = await self.bot.db.fetch(query, payload.guild_id)
        if payload.message_id not in [role['message_id'] for role in reaction_roles]:
            return
        else:
            guild_id = payload.guild_id
            guild = None
            query = "SELECT * FROM reaction_roles JOIN emoji_role ON emoji_role.reaction_role_id = reaction_roles.id WHERE reaction_roles.guild_id = $1 AND reaction_roles.message_id = $2"
            records = await self.bot.db.fetch(query, guild_id, payload.message_id)
            role = None
            records = {record['emoji']: record['role_id'] for record in records}
            role_id = records.get(str(payload.emoji))
            if role_id is not None:
                guild = self.bot.get_guild(guild_id)
                role = guild.get_role(role_id)
            if role is not None:
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role, reason="Reaction Role")
                try:
                    await member.send(f'Removed the **{role.name}** role!')
                except:
                    pass

def setup(bot):
    bot.add_cog(ReactionRoles(bot))

