import discord
from discord.ext import commands

from tabulate import tabulate

from .utils.ranking import rank_picture
from .utils.custom_embeds import failure_embed

import asyncio
from io import BytesIO

from .utils.ranking import get_user_level_data, humanize


class Levelling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Check your current level and rank throughout all server the bot is in.",
                      aliases=['level', 'lvl'])
    async def rank(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        if member.bot:
            return await ctx.send(embed=await failure_embed(title="You can't check the rank of a bot."))
        user = await self.bot.db.get_user(id=member.id)
        if user is not None:
            pfp = member.avatar_url_as(size=256, static_format="png")
            img_data = BytesIO(await pfp.read())
            loop = asyncio.get_event_loop()
            query_guild = f"""
                        WITH ordered_users AS (
                          SELECT
                            id,
                            ROW_NUMBER() OVER (ORDER BY total_xp DESC) rank
                          FROM users)
                          SELECT rank FROM ordered_users WHERE ordered_users.id = $1;
                        """
            record = await self.bot.db.fetchrow(query_guild, member.id)
            rank = record['rank']
            image = await loop.run_in_executor(None, rank_picture, user, str(member), rank, img_data)
            await ctx.send(file=discord.File(filename="rank.png", fp=image))
            image.seek(0)
        else:
            await ctx.send(embed=await failure_embed("Requested member was not found."))

    @commands.command(aliases=['lb', 'rankings'])
    async def leaderboard(self, ctx, *, lb_type=None):
        query = "SELECT id, messages_sent, in_hand, garrix_coins, total_xp FROM users "
        help_categories = """Available Categories:
        `xp`, `total xp`, `experience`, `levels`, `level`, `lvl` - **Ordered on your level in the server.**
        `coins`, `coin`, `currency`, `garrix coins` - **Ordered by the amount of coins you have.**
        `msgs`, `msg`, `total messages`, `all messages` - **Ordered by the number of messages you have sent.**
        """
        lb = None
        lb_name = None
        if lb_type in ["coins", "coin", "currency", "garrix coins"]:
            query += "ORDER BY garrix_coins DESC LIMIT 10"
            records = await self.bot.db.fetch(query)
            lb_name = "Coins"
            lb = []
            for record in records:
                member = ctx.guild.get_member(record['id'])
                if member is None:
                    continue
                lb.append([member, (record['garrix_coins'] + record['in_hand'])])

        elif lb_type in ["xp", "total xp", "experience", "levels", "level", "lvl", "rank"]:
            query += "ORDER BY total_xp DESC LIMIT 10"
            records = await self.bot.db.fetch(query)
            lb_name = "Levels"
            lb = []
            for record in records:
                member = ctx.guild.get_member(record['id'])
                if member is None:
                    continue
                lb.append([member, get_user_level_data(record['total_xp'])['lvl']])

        elif lb_type in ["msgs", "msg", "total messages", "all messages"]:
            query += "ORDER BY messages_sent DESC LIMIT 10"
            records = await self.bot.db.fetch(query)
            lb_name = "Messages"
            lb = []
            for record in records:
                member = ctx.guild.get_member(record['id'])
                if member is None:
                    continue
                lb.append([member, humanize(record['messages_sent'])])

        else:
            return await ctx.send(embed=discord.Embed(
                title=f"{'That category of leaderboard does not exist.' if lb_type is not None else 'Please specify a category for leaderboard'}",
                description=help_categories, color=discord.Colour.teal()))

        return await ctx.send(f'>>> ```prolog\n{tabulate(lb, headers=("User", lb_name,), tablefmt="fancy_grid")}\n```')


def setup(bot):
    bot.add_cog(Levelling(bot))