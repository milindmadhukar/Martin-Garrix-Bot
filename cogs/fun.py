import asyncio
import random
import traceback
import typing
from difflib import SequenceMatcher

import discord
from discord.ext import commands

from core.MartinBotBase import MartinGarrixBot
from utils.command_helpers import get_lyrics_embed
from utils.helpers import failure_embed, success_embed, parse_amount


class Fun(commands.Cog):
    def __init__(self, bot: MartinGarrixBot):
        self.bot = bot

    async def get_songs(self):
        query = "SELECT name FROM songs WHERE lyrics IS NOT NULL"
        songs = await self.bot.database.fetch(query)
        return songs

    # async def lyrics_autocomplete(
    #         interaction: discord.Interaction,
    #         current: str,
    #         ) -> typing.List[discord.app_commands.Choice]:
    #     songs = await self.get_songs()
    #     return [
    #         discord.app_commands.Choice(name=song["name"], value=song["name"])
    #         for song in songs
    #         if current.lower() in song["name"].lower()
    #     ]

    @commands.hybrid_command(
        name="lyrics",
        help="Get the lyrics of any Martin Garrix, Area 21, GRX or YTRAM song.",
    )
    # @discord.app_commands.autocomplete(name=lyrics_autocomplete, description="Name of the song")
    async def lyrics(
        self,
        ctx: commands.Context,
        name: str,
    ):
        query = "SELECT * FROM songs WHERE name LIKE $1"
        song_data = await self.bot.database.fetchrow(query, name)

        if song_data is None:
            return await ctx.send(
                embed=await failure_embed(title="No such song found."), ephemeral=True
            )

        pager = commands.Paginator()

        for line in song_data["lyrics"].split("\n"):
            pager.add_line(line=line)

        embed_count = 0
        for page in pager.pages:
            embed = get_lyrics_embed(page)

            if embed_count == 0:
                embed.title = f"{song_data['alias']} - {song_data['name']}"
                if song_data["thumbnail_url"] is not None:
                    embed.set_thumbnail(url=song_data["thumbnail_url"])

            await ctx.send(embed=embed)
            embed_count += 1

    @commands.hybrid_command(name="quiz", help="Guess the song title from the lyrics.")
    @discord.app_commands.choices(
        difficulty=[
            discord.app_commands.Choice(name="Easy", value="easy"),
            discord.app_commands.Choice(name="Medium", value="medium"),
            discord.app_commands.Choice(name="Hard", value="hard"),
            discord.app_commands.Choice(name="Extreme", value="extreme"),
        ]
    )
    @commands.cooldown(1, 10 * 60, commands.BucketType.user)
    async def quiz(
        self,
        ctx: commands.Context,
        difficulty: str,
    ):
        if difficulty not in ["easy", "medium", "hard", "extreme"]:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                embed=await failure_embed(
                    "Invalid difficulty. Please choose from `easy`, `medium`, `hard` or `extreme`"
                ),
                ephemeral=True,
                delete_after=10,
            )

        # Check if it is a command interaction

        ctx.defer()

        query = "SELECT * FROM songs WHERE lyrics IS NOT NULL ORDER BY RANDOM() LIMIT 1"
        if difficulty == "easy":
            query = query[:44] + " AND alias = 'Martin Garrix'" + query[44:]
        song = await self.bot.database.fetchrow(query)
        lines = song["lyrics"].split("\n")
        lyrics = ""
        difficulty_lines = {"easy": 4, "medium": 3, "hard": 2, "extreme": 1}
        start = 0
        end = len(lines) - 1 - difficulty_lines.get(difficulty, 3)
        line_number = random.randint(start, end)
        tries = 0
        while lyrics == "":
            tries += 1
            lyrics = "\n".join(
                lines[line_number : line_number + difficulty_lines.get(difficulty, 3)]
            )
            if tries > 10:
                break
        if not lyrics:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                embed=await failure_embed(
                    "Oops, something went wrong. Please try again."
                ),
                ephemeral=True,
                delete_after=10,
            )

        embed = discord.Embed(
            title=f"Guess the song title from the lyrics! ({difficulty.title()})",
            description="Guess the song name within 45 seconds.",
            colour=discord.Colour.gold(),
        ).add_field(name="Lyrics", value=lyrics)

        await ctx.send(embed=embed)

        embed = None
        similarity = None

        try:
            guess = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
                timeout=30,
            )
            similarity = SequenceMatcher(
                None,
                song["name"].lower().replace(" ", ""),
                guess.content.lower().replace(" ", ""),
            ).ratio()

        except asyncio.TimeoutError:
            embed = await failure_embed("Oops, you ran out of time")

        if similarity is not None:
            if similarity > 0.7:
                earning_dict = {"easy": 50, "medium": 100, "hard": 150, "extreme": 200}
                earning = earning_dict.get(difficulty)
                embed = discord.Embed(
                    title=f"<a:tick:810462879374770186> Your guess is correct and you earned {earning} Garrix Coins.",
                    colour=discord.Colour.green(),
                )
                user = await self.bot.database.get_user(ctx.author.id)
                if user is None:
                    return
                await user.add_coins(earning)

            else:
                embed = discord.Embed(
                    title=f"<a:cross:810462920810561556>  Your guess is incorrect",
                    colour=discord.Colour.red(),
                )

        embed.add_field(name="Song Name", value=f"{song['alias']} - {song['name']}")
        if song["thumbnail_url"] is not None:
            embed.set_thumbnail(url=song["thumbnail_url"])

        await ctx.send(embed=embed)

    @quiz.error
    async def quiz_error(self, interaction: discord.Interaction, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="You are currently on cooldown.",
                description=f" This game can only be played once in 10 minutes."
                f"\nTry again in {int(error.retry_after)} seconds",
                color=discord.Colour.red(),
            )
            return await interaction.send(embed=embed, ephemeral=True)
        else:
            print(traceback.format_exception(type(error), error, error.__traceback__))

    @commands.hybrid_command(
        name="balance",
        aliases=["bal"],
        help="Check you account balance for Garrix coins",
    )
    async def balance(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        query = "SELECT in_hand, garrix_coins FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, member.id)
        in_hand = record["in_hand"]
        garrix_coins = record["garrix_coins"]

        embed = (
            discord.Embed(title="Garrix Bank", colour=discord.Colour.orange())
            .add_field(name="In hand", value=in_hand)
            .add_field(name="In Safe", value=garrix_coins)
            .set_thumbnail(url=member.avatar.with_size(256))
        )

        return await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="withdraw",
        aliases=["with"],
        help="Withdraw Garrix coins from safe to hold in hand.",
    )
    async def withdraw(self, ctx: commands.Context, amount: str):
        query = "SELECT garrix_coins FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, ctx.author.id)
        garrix_coins = record["garrix_coins"]
        amt = parse_amount(amount, garrix_coins)
        print("The amount is", amt)
        if amt > garrix_coins:
            return await ctx.send(
                embed=await failure_embed(
                    f"Not enough balance to withdraw {amt} Garrix coins."
                )
            )

        if amt == -1 or amt <= 0:
            return await ctx.send(
                embed=await failure_embed(
                    "Invalid amount. Please specify a valid amount to withdraw."
                )
            )

        query = "UPDATE users SET in_hand = in_hand + $2, garrix_coins = garrix_coins - $2 WHERE id = $1"
        await self.bot.database.execute(query, ctx.author.id, amt)
        return await ctx.send(
            embed=await success_embed(f"Successfully withdrew {amt} coins.")
        )

    @commands.hybrid_command(
        name="deposit", aliases=["dep"], help="Deposit Garrix coins from hand to safe."
    )
    async def deposit(self, ctx: commands.Context, amount: str):
        query = "SELECT in_hand FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, ctx.author.id)
        in_hand = record["in_hand"]
        amt = parse_amount(amount, in_hand)
        if amt == -1 or amt <= 0:
            return await ctx.send(
                embed=await failure_embed(
                    "Invalid amount. Please specify a valid amount to deposit."
                )
            )

        if amt > in_hand:
            return await ctx.send(
                embed=await failure_embed(
                    "Can't deposit more than what you hold in your hand."
                )
            )

        query = "UPDATE users SET in_hand = in_hand - $2, garrix_coins = garrix_coins + $2 WHERE id = $1 "
        await self.bot.database.execute(query, ctx.author.id, amt)
        return await ctx.send(
            embed=await success_embed(f"Successfully deposited {amt} coins.")
        )

    @commands.hybrid_command(name="give", help="Give Garrix coins to another user.")
    async def give(self, ctx: commands.Context, member: discord.Member, amount: str):
        query = "SELECT in_hand FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, ctx.author.id)
        if record is None:
            print("No such user?")
            return
        in_hand = record["in_hand"]
        amt = parse_amount(amount, in_hand)
        if amt > in_hand:
            return await ctx.send(
                embed=await failure_embed(
                    "Can't give more than what you hold in your hand. Try withdrawing if you have the balance"
                )
            )
        if amt <= 0:
            return await ctx.send(
                embed=await failure_embed(f"Please specify a valid amount to give.")
            )
        query = "UPDATE users SET in_hand = in_hand + $2 WHERE id = $1"
        await self.bot.database.execute(query, member.id, amt)
        query = "UPDATE users SET in_hand = in_hand - $2 WHERE id = $1"
        await self.bot.database.execute(query, ctx.author.id, amt)
        return await ctx.send(
            embed=await success_embed(
                f"Successfully gave {amt} coins to {member.display_name}."
            )
        )

    @commands.cooldown(1, 3 * 60 * 60, commands.BucketType.user)
    @commands.hybrid_command(name="rob", help="Rob Garrix coins from another user.")
    async def rob(self, ctx: commands.Context, member: discord.Member):
        if member.id == ctx.author.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=await failure_embed("You can't rob yourself."))

        query = "SELECT in_hand FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, member.id)
        in_hand = record["in_hand"]
        if in_hand < 200:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                embed=await failure_embed(
                    "Member needs to have atleast 200 Garrix coins in hand to be robbed."
                )
            )
        is_going_to_be_robbed = random.choice([True, False, False, False, False])
        # is_going_to_be_robbed = True
        if is_going_to_be_robbed:
            amount_robbed = random.randint(200, in_hand)
            query = "UPDATE users SET in_hand = in_hand - $2 WHERE id = $1"
            await self.bot.database.execute(query, member.id, amount_robbed)
            query = "UPDATE users SET in_hand = in_hand + $2 WHERE id = $1"
            await self.bot.database.execute(query, ctx.author.id, amount_robbed)
            return await ctx.send(
                f"Successfully robbed {amount_robbed} Garrix coins from {member.mention}"
            )
        else:
            query = "UPDATE users SET in_hand = in_hand - 200 WHERE id = $1"
            await self.bot.database.execute(query, ctx.author.id)
            return await ctx.message.reply(
                "🚔 You have been caught stealing and lost 200 Garrix coins"
            )

    @rob.error
    async def rob_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="You are currently on cooldown.",
                description=f" Woah thief, you can only rob once in 3 hours.\nTry again "
                f"in {int(error.retry_after)} seconds",
                color=discord.Colour.red(),
            )
            return await ctx.send(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)
            print(traceback.format_exception(type(error), error, error.__traceback__))


async def setup(bot):
    await bot.add_cog(Fun(bot))
