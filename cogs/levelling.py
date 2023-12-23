from os import name
import typing
import discord
from discord.ext import commands

from tabulate import tabulate

from core.MartinBotBase import MartinGarrixBot
from utils.helpers import rank_picture, failure_embed

import asyncio
from io import BytesIO


from utils.helpers import get_user_level_data, humanize


class Levelling(commands.Cog):
    def __init__(self, bot: MartinGarrixBot):
        self.bot = bot

    @commands.hybrid_command(
        name="rank",
        help="Check the current level and rank of a member in the server",
    )
    async def rank(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        if member.bot:
            return await ctx.send(
                embed=await failure_embed(
                    title="You can't check the rank of a bot.",
                    ephemeral=True,
                    delete_after=10,
                )
            )

        user = await self.bot.database.get_user(member.id)
        if user is not None:
            await ctx.defer()

            pfp = member.display_avatar.with_size(256).with_static_format("png")
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
            record = await self.bot.database.fetchrow(query_guild, member.id)
            rank = record["rank"]
            image = await loop.run_in_executor(
                None, rank_picture, user, str(member), rank, img_data
            )
            await ctx.send(file=discord.File(filename="rank.png", fp=image))
            image.seek(0)
        else:
            await ctx.send(
                embed=await failure_embed("Requested member was not found."),
                ephemeral=True,
                delete_after=10,
            )

    @commands.hybrid_command(
        name="leaderboard", help="Check the leaderboard of various categories"
    )
    @discord.app_commands.choices(
        leaderboard_type=[
            discord.app_commands.Choice(name="Levels", value="levels"),
            discord.app_commands.Choice(name="Messages", value="messages"),
            discord.app_commands.Choice(name="Coins", value="coins"),
            discord.app_commands.Choice(name="Coins in hand", value="coins_in_hand"),
        ]
    )
    async def leaderboard(self, ctx: commands.Context, leaderboard_type: str):
        query = "SELECT id, messages_sent, in_hand, garrix_coins, total_xp FROM users "
        lb_name = ""
        lb = []
        if leaderboard_type == "coins":
            query += "ORDER BY garrix_coins DESC LIMIT 10"
            records = await self.bot.database.fetch(query)
            lb_name = "Coins"
            for record in records:
                member = self.bot.guild.get_member(record["id"])
                if member is None:
                    continue
                lb.append([member, record["garrix_coins"]])
                print(lb)

        elif leaderboard_type == "coins_in_hand":
            query += "ORDER BY in_hand DESC LIMIT 10"
            records = await self.bot.database.fetch(query)
            lb_name = "Coins In Hand"
            for record in records:
                member = self.bot.guild.get_member(record["id"])
                if member is None:
                    continue
                lb.append([member, record["in_hand"]])

        elif leaderboard_type == "levels":
            query += "ORDER BY total_xp DESC LIMIT 10"
            records = await self.bot.database.fetch(query)
            lb_name = "Levels"
            for record in records:
                member = self.bot.guild.get_member(record["id"])
                if member is None:
                    continue
                lb.append([member, get_user_level_data(record["total_xp"])["lvl"]])

        elif leaderboard_type == "messages":
            query += "ORDER BY messages_sent DESC LIMIT 10"
            records = await self.bot.database.fetch(query)
            lb_name = "Messages"
            for record in records:
                member = self.bot.guild.get_member(record["id"])
                if member is None:
                    continue
                lb.append([member, humanize(record["messages_sent"])])

        else:
            return await ctx.send(
                embed=await failure_embed(
                    title="Please specify a valid leaderboard type",
                    description=f"{leaderboard_type} is not a valid leaderboard type.\nValid leaderboard types are: `levels`, `messages`, `coins`, `coins_in_hand`",
                ),
                ephemeral=True,
                delete_after=10,
            )

        return await ctx.send(
            f'>>> ```prolog\n{tabulate(lb, headers=("User", lb_name,), tablefmt="fancy_grid")}\n```'
        )


async def setup(bot):
    await bot.add_cog(Levelling(bot))
