import asyncio
import random
import traceback
import typing
from difflib import SequenceMatcher

import disnake
from disnake.ext import commands

from core.MartinBotBase import MartinGarrixBot
from utils.command_helpers import get_lyrics_embed
from utils.helpers import failure_embed, success_embed, parse_amount

Quiz_difficulties = commands.option_enum(choices=["easy", "medium", "hard", "extreme"])


class Fun(commands.Cog):
    def __init__(self, bot: MartinGarrixBot):
        self.bot = bot

    @commands.command(
        help="Get the lyrics of any Martin Garrix, Area 21, GRX or YTRAM song."
    )
    async def lyrics(self, ctx: commands.Context, *, song_name: str):
        query = "SELECT * FROM songs WHERE name LIKE $1"
        song_data = await self.bot.database.fetchrow(query, song_name)

        if song_data is None:
            return await ctx.send(
                embed=await failure_embed(title="No such song found.")
            )

        return await ctx.send(embed=get_lyrics_embed(song_data))

    @commands.slash_command(
        name="lyrics",
        description="Get the lyrics of any Martin Garrix, Area 21, GRX or YTRAM song.",
    )
    async def lyrics_slash(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        song_name: str = commands.Param(description="Enter the name of the song."),
    ):

        query = "SELECT * FROM songs WHERE name LIKE $1"
        song_data = await self.bot.database.fetchrow(query, song_name)

        if song_data is None:
            return await interaction.send_message(
                embed=await failure_embed(title="No such song found."),
                ephemeral=True,
            )

        return await interaction.send_message(embed=get_lyrics_embed(song_data))

    @commands.command()
    @commands.cooldown(1, 10 * 60, commands.BucketType.user)
    async def quiz(
        self, ctx: commands.Context, difficulty: lambda inp: inp.lower() = None
    ):
        if difficulty is None or difficulty not in [
            "easy",
            "medium",
            "hard",
            "extreme",
        ]:
            embed = disnake.Embed(
                title="Please choose an appropriate difficulty level.",
                description="Your choices are:\n**easy** : "
                "50 garrix coins\n**medium** : 100 garrix coins\n**hard** : "
                "150 garrix coins\n**extreme** : 200 garrix coins",
                color=disnake.Colour.teal(),
            )
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=embed)

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
            return await ctx.send("Some error occurred, please try again.")

        embed = disnake.Embed(
            title=f"Guess the song title from the lyrics! ({difficulty.title()})",
            description="Guess the song name within 45 seconds.",
            colour=disnake.Colour.gold(),
        ).add_field(name="Lyrics", value=lyrics)

        await ctx.message.reply(embed=embed, mention_author=False)

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
                embed = disnake.Embed(
                    title=f"<a:tick:810462879374770186> Your guess is correct and you earned {earning} Garrix Coins.",
                    colour=disnake.Colour.green(),
                )
                user = await self.bot.database.get_user(ctx.author.id)
                if user is None:
                    return
                await user.add_coins(earning)

            else:
                embed = disnake.Embed(
                    title=f"<a:cross:810462920810561556>  Your guess is incorrect",
                    colour=disnake.Colour.red(),
                )

        embed.add_field(name="Song Name", value=f"{song['alias']} - {song['name']}")
        if song["thumbnail_url"] is not None:
            embed.set_thumbnail(url=song["thumbnail_url"])

        await ctx.send(embed=embed)

    @quiz.error
    async def quiz_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(
                title="You are currently on cooldown.",
                description=f" This game can only be played once in 10 minutes."
                f"\nTry again in {int(error.retry_after)} seconds",
                color=disnake.Colour.red(),
            )
            return await ctx.send(embed=embed)
        else:
            print(traceback.format_exception(type(error), error, error.__traceback__))

    # @commands.slash_command(
    #     name="quiz", description="Solve a Martin Garrix Quiz question."
    # )
    @commands.cooldown(1, 10 * 60, commands.BucketType.user)
    async def quiz_slash(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        difficulty: Quiz_difficulties,
    ):
        await interaction.response.defer()

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
            interaction.application_command.reset_cooldown(interaction)
            return await interaction.response.send_message(
                embed=await failure_embed("Some error occurred, please try again."),
                ephemeral=True,
            )

        embed = disnake.Embed(
            title=f"Guess the song title from the lyrics! ({difficulty.title()})",
            description="Guess the song name within 45 seconds.",
            colour=disnake.Colour.gold(),
        ).add_field(name="Lyrics", value=lyrics)

        await interaction.send(embed=embed)

        embed = None
        similarity = None

        try:
            guess = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == interaction.author.id
                and m.channel.id == interaction.channel.id,
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
                embed = disnake.Embed(
                    title=f"<a:tick:810462879374770186> Your guess is correct and you earned {earning} Garrix Coins.",
                    colour=disnake.Colour.green(),
                )
                user = await self.bot.database.get_user(interaction.author.id)
                if user is None:
                    return
                await user.add_coins(earning)

            else:
                embed = disnake.Embed(
                    title=f"<a:cross:810462920810561556>  Your guess is incorrect",
                    colour=disnake.Colour.red(),
                )

        embed.add_field(name="Song Name", value=f"{song['alias']} - {song['name']}")
        if song["thumbnail_url"] is not None:
            embed.set_thumbnail(url=song["thumbnail_url"])

        await interaction.send(embed=embed)

    @quiz_slash.error
    async def quiz_error(
        self, interaction: disnake.ApplicationCommandInteraction, error: Exception
    ):
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(
                title="You are currently on cooldown.",
                description=f" This game can only be played once in 10 minutes."
                f"\nTry again in {int(error.retry_after)} seconds",
                color=disnake.Colour.red(),
            )
            return await interaction.send(embed=embed, ephemeral=True)
        else:
            print(traceback.format_exception(type(error), error, error.__traceback__))

    @commands.command(
        help="Check you account balance for Garrix coins", aliases=["bal"]
    )
    async def balance(self, ctx: commands.Context, member: disnake.Member = None):
        member = member or ctx.author
        query = "SELECT in_hand, garrix_coins FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, member.id)
        in_hand = record["in_hand"]
        garrix_coins = record["garrix_coins"]
        embed = (
            disnake.Embed(title="Garrix Bank", colour=disnake.Colour.orange())
            .add_field(name="In hand", value=in_hand)
            .add_field(name="In Safe", value=garrix_coins)
            .set_thumbnail(url=member.avatar.with_size(256))
        )

        return await ctx.send(embed=embed)

    @commands.slash_command(
        name="balance", description="Check you account balance for Garrix coins"
    )
    async def balance_slash(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        member: typing.Optional[disnake.Member] = commands.Param(
            None, description="Enter the member whose balance you want to check."
        ),
    ):
        member = member or interaction.author
        query = "SELECT in_hand, garrix_coins FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, member.id)
        in_hand = record["in_hand"]
        garrix_coins = record["garrix_coins"]
        embed = (
            disnake.Embed(title="Garrix Bank", colour=disnake.Colour.orange())
            .add_field(name="In hand", value=in_hand)
            .add_field(name="In Safe", value=garrix_coins)
            .set_thumbnail(url=member.avatar.with_size(256))
        )

        return await interaction.send(embed=embed)

    @commands.command(
        help="Withdraw Garrix coins from safe to hold in hand.", aliases=["with", "wd"]
    )
    async def withdraw(self, ctx: commands.Context, amount: str):
        query = "SELECT garrix_coins FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, ctx.author.id)
        garrix_coins = record["garrix_coins"]
        amt = parse_amount(amount, garrix_coins)
        if amt > garrix_coins:
            return await ctx.send(
                embed=await failure_embed(
                    f"Not enough balance to withdraw {amt} Garrix coins."
                )
            )
        if amt <= 0:
            return await ctx.send(
                embed=await failure_embed(f"Please specify a valid amount to withdraw.")
            )
        query = "UPDATE users SET in_hand = in_hand + $2, garrix_coins = garrix_coins - $2 WHERE id = $1"
        await self.bot.database.execute(query, ctx.author.id, amt)
        return await ctx.send(
            embed=await success_embed(f"Successfully withdrew {amt} coins.")
        )

    @commands.slash_command(
        name="withdraw", description="Withdraw Garrix coins from safe to hold in hand."
    )
    async def withdraw_slash(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        amount: str = commands.Param(description="Enter the amount to withdraw."),
    ):
        query = "SELECT garrix_coins FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, interaction.author.id)
        garrix_coins = record["garrix_coins"]
        amt = parse_amount(amount, garrix_coins)
        if amt > garrix_coins:
            return await interaction.send(
                embed=await failure_embed(
                    f"Not enough balance to withdraw {amt} Garrix coins."
                ),
                ephemeral=True,
            )
        if amt <= 0:
            return await interaction.send(
                embed=await failure_embed(
                    f"Please specify a valid amount to withdraw."
                ),
                ephemeral=True,
            )
        query = "UPDATE users SET in_hand = in_hand + $2, garrix_coins = garrix_coins - $2 WHERE id = $1"
        await self.bot.database.execute(query, interaction.author.id, amt)
        return await interaction.send(
            embed=await success_embed(f"Successfully withdrew {amt} coins.")
        )

    @commands.command(
        help="Deposit Garrix coins from hand to safe.", aliases=["depo", "dep"]
    )
    async def deposit(self, ctx: commands.Context, amount: str):
        query = "SELECT in_hand FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, ctx.author.id)
        in_hand = record["in_hand"]
        amt = parse_amount(amount, in_hand)
        if amt > in_hand:
            return await ctx.send(
                embed=await failure_embed(
                    "Can't deposit more than what you hold in your hand."
                )
            )

        if amt <= 0 or amt == 0:
            msg = "You are not holding any coins in hand."
        else:
            msg = "You either have negative balance or specified an invalid amount."
            return await ctx.send(embed=await failure_embed(msg))
        query = "UPDATE users SET in_hand = in_hand - $2, garrix_coins = garrix_coins + $2 WHERE id = $1 "
        await self.bot.database.execute(query, ctx.author.id, amt)
        return await ctx.send(
            embed=await success_embed(f"Successfully deposited {amt} coins.")
        )

    @commands.slash_command(
        name="deposit", description="Deposit Garrix coins from hand to safe."
    )
    async def deposit_slash(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        amount: str = commands.Param(description="Enter the amount to deposit."),
    ):
        query = "SELECT in_hand FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, interaction.author.id)
        in_hand = record["in_hand"]
        amt = parse_amount(amount, in_hand)
        if amt > in_hand:
            return await interaction.send_message(
                embed=await failure_embed(
                    "Can't deposit more than what you hold in your hand."
                ),
                ephemeral=True,
            )

        if amt <= 0 or amt == 0:
            msg = "You are not holding any coins in hand."
        else:
            msg = "You either have negative balance or specified an invalid amount."
            return await interaction.send(
                embed=await failure_embed(msg), ephemeral=True
            )
        query = "UPDATE users SET in_hand = in_hand - $2, garrix_coins = garrix_coins + $2 WHERE id = $1 "
        await self.bot.database.execute(query, interaction.author.id, amt)
        return await interaction.send(
            embed=await success_embed(f"Successfully deposited {amt} coins.")
        )

    @commands.command(help="Give Garrix coins to a member.")
    async def give(self, ctx: commands.Context, member: disnake.Member, amount: str):
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

    @commands.slash_command(name="give", description="Give Garrix coins to a member.")
    async def give_slash(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            description="Enter the member whom you want to give coins."
        ),
        amount: str = commands.Param(description="Enter the amount to deposit."),
    ):
        query = "SELECT in_hand FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, interaction.author.id)
        if record is None:
            return interaction.send(
                embed=await failure_embed("No such member found."), ephemeral=True
            )
        in_hand = record["in_hand"]
        amt = parse_amount(amount, in_hand)
        if amt > in_hand:
            return await interaction.send(
                embed=await failure_embed(
                    "Can't give more than what you hold in your hand. Try withdrawing if you have sufficient balance."
                ),
                ephemeral=True,
            )
        if amt <= 0:
            return await interaction.send(
                embed=await failure_embed(f"Please specify a valid amount to give."),
                ephemeral=True,
            )
        query = "UPDATE users SET in_hand = in_hand + $2 WHERE id = $1"
        await self.bot.database.execute(query, member.id, amt)
        query = "UPDATE users SET in_hand = in_hand - $2 WHERE id = $1"
        await self.bot.database.execute(query, interaction.author.id, amt)
        return await interaction.send(
            embed=await success_embed(
                f"Successfully gave {amt} coins to {member.display_name}."
            )
        )

    # TODO: Give and withdraw coins by admins

    @commands.cooldown(1, 3 * 60 * 60, commands.BucketType.user)
    @commands.command(help="Steal Garrix coins from another member")
    async def rob(self, ctx: commands.Context, member: disnake.Member):
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
            embed = disnake.Embed(
                title="You are currently on cooldown.",
                description=f" Woah thief, you can only rob once in 3 hours.\nTry again "
                f"in {int(error.retry_after)} seconds",
                color=disnake.Colour.red(),
            )
            return await ctx.send(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)
            print(traceback.format_exception(type(error), error, error.__traceback__))

    @commands.cooldown(1, 3 * 60 * 60, commands.BucketType.user)
    # @commands.slash_command(
    #     name="rob", description="Steal Garrix coins from another member."
    # )
    async def rob_slash(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(description="Enter the member to rob."),
    ):
        await interaction.response.defer(message="Robbing in progress....")
        if member.id == interaction.author.id:
            interaction.application_command.reset_cooldown(interaction)
            return await interaction.send(
                embed=await failure_embed("You can't rob yourself."), ephemeral=True
            )

        query = "SELECT in_hand FROM users WHERE id = $1"
        record = await self.bot.database.fetchrow(query, member.id)
        in_hand = record["in_hand"]
        if in_hand < 200:
            interaction.application_command.reset_cooldown(interaction)
            return await interaction.send(
                embed=await failure_embed(
                    "Member needs to have atleast 200 Garrix coins in hand to be robbed."
                ),
                ephemeral=True,
            )
        is_going_to_be_robbed = random.choice([True, False, False, False, False])
        # is_going_to_be_robbed = True
        if is_going_to_be_robbed:
            amount_robbed = random.randint(200, in_hand)
            query = "UPDATE users SET in_hand = in_hand - $2 WHERE id = $1"
            await self.bot.database.execute(query, member.id, amount_robbed)
            query = "UPDATE users SET in_hand = in_hand + $2 WHERE id = $1"
            await self.bot.database.execute(query, interaction.author.id, amount_robbed)
            return await interaction.send(
                f"Successfully robbed {amount_robbed} Garrix coins from {member.mention}"
            )
        else:
            query = "UPDATE users SET in_hand = in_hand - 200 WHERE id = $1"
            await self.bot.database.execute(query, interaction.author.id)
            return await interaction.send(
                "🚔 You have been caught stealing and lost 200 Garrix coins"
            )

    @rob_slash.error
    async def rob_error(
        self, interaction: disnake.ApplicationCommandInteraction, error: Exception
    ):
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(
                title="You are currently on cooldown.",
                description=f" Woah thief, you can only rob once in 3 hours.\nTry again "
                f"in {int(error.retry_after)} seconds",
                color=disnake.Colour.red(),
            )
            return await interaction.send(embed=embed, ephemeral=True)
        else:
            interaction.application_command.reset_cooldown(interaction)
            print(traceback.format_exception(type(error), error, error.__traceback__))


    # TODO: Fix quiz and rob.


def setup(bot):
    bot.add_cog(Fun(bot))
