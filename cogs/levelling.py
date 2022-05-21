import typing
import disnake
from disnake.ext import commands
from disnake.ext.commands.params import Param
from disnake.interactions.application_command import ApplicationCommandInteraction
from disnake.member import Member

from tabulate import tabulate

from core.MartinBotBase import MartinGarrixBot
from utils.helpers import rank_picture, failure_embed

import asyncio
from io import BytesIO

from utils.helpers import get_user_level_data, humanize


class Levelling(commands.Cog):
    def __init__(self, bot: MartinGarrixBot):
        self.bot = bot

    @commands.command(
        help="Check the current level and rank of a member in the server",
        aliases=["level", "lvl"],
    )
    async def rank(self, ctx: commands.Context, member: disnake.Member = None):
        member = member or ctx.author
        if member.bot:
            return await ctx.send(
                embed=await failure_embed(title="You can't check the rank of a bot.")
            )
        user = await self.bot.database.get_user(member.id)
        if user is not None:
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
            await ctx.send(file=disnake.File(filename="rank.png", fp=image))
            image.seek(0)
        else:
            await ctx.send(embed=await failure_embed("Requested member was not found."))

    @commands.slash_command(
        name="rank",
        description="Check the current level and rank of a member in the server.",
    )
    async def rank_slash(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: typing.Optional[disnake.Member] = commands.Param(
            None, description="Enter the member whose rank you want to check."
        ),
    ):
        member = member or inter.author
        if member.bot:
            return await inter.response.send_message(
                embed=await failure_embed(title="You can't check the rank of a bot."),
                ephemeral=True,
            )
        user = await self.bot.database.get_user(member.id)
        if user is not None:
            await inter.response.defer()
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
            await inter.edit_original_message(file=disnake.File(filename="rank.png", fp=image))
            image.seek(0)
        else:
            await inter.edit_original_message(embed=await failure_embed("Requested member was not found."))

    @commands.command(aliases=["lb", "rankings"])
    async def leaderboard(self, ctx: commands.Context, *, lb_type: str = None):
        query = "SELECT id, messages_sent, in_hand, garrix_coins, total_xp FROM users "
        help_categories = """Available Categories:
        `xp`, `total xp`, `experience`, `levels`, `level`, `lvl` - **Ordered on your level in the server.**
        `coins`, `coin`, `currency`, `garrix coins` - **Ordered by the amount of coins you have.**
        `msgs`, `msg`, `total messages`, `all messages` - **Ordered by the number of messages you have sent.**
        `hand`, `in hand` - **Ordered by the amount of Garrix coins in hand. Useful for robbing.**
        """
        if lb_type in ["coins", "coin", "currency", "garrix coins"]:
            query += "ORDER BY garrix_coins DESC LIMIT 10"
            records = await self.bot.database.fetch(query)
            lb_name = "Coins"
            lb = []
            for record in records:
                member = ctx.guild.get_member(record["id"])
                if member is None:
                    continue
                lb.append([member, (record["garrix_coins"] + record["in_hand"])])

        elif lb_type in [
            "xp",
            "total xp",
            "experience",
            "levels",
            "level",
            "lvl",
            "rank",
        ]:
            query += "ORDER BY total_xp DESC LIMIT 10"
            records = await self.bot.database.fetch(query)
            lb_name = "Levels"
            lb = []
            for record in records:
                member = ctx.guild.get_member(record["id"])
                if member is None:
                    continue
                lb.append([member, get_user_level_data(record["total_xp"])["lvl"]])

        elif lb_type in ["msgs", "msg", "total messages", "all messages"]:
            query += "ORDER BY messages_sent DESC LIMIT 10"
            records = await self.bot.database.fetch(query)
            lb_name = "Messages"
            lb = []
            for record in records:
                member = ctx.guild.get_member(record["id"])
                if member is None:
                    continue
                lb.append([member, humanize(record["messages_sent"])])

        elif lb_type in ["hand", "in hand"]:
            query += "ORDER BY in_hand DESC LIMIT 10"
            records = await self.bot.database.fetch(query)
            lb_name = "Coins in hand"
            lb = []
            for record in records:
                member = ctx.guild.get_member(record["id"])
                if member is None:
                    continue
                lb.append([member, record["in_hand"]])

        else:
            return await ctx.send(
                embed=disnake.Embed(
                    title=f"{'That category of leaderboard does not exist.' if lb_type is not None else 'Please specify a category for leaderboard'}",
                    description=help_categories,
                    color=disnake.Colour.teal(),
                )
            )

        return await ctx.send(
            f'>>> ```prolog\n{tabulate(lb, headers=("User", lb_name,), tablefmt="fancy_grid")}\n```'
        )


def setup(bot):
    bot.add_cog(Levelling(bot))
