import disnake
from disnake.ext import commands
import random
import asyncio
from difflib import SequenceMatcher

from core.MartinBotBase import MartinGarrixBot
from utils.helpers import failure_embed, success_embed, parse_amount


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

        embed = disnake.Embed(
            title=f'{song_data["alias"]} - {song_data["name"]}',
            description=song_data["lyrics"][:4096],
            color=disnake.Colour.orange(),
        )

        if song_data["thumbnail_url"] is not None:
            embed.set_thumbnail(url=song_data["thumbnail_url"])

        return await ctx.send(embed=embed)

    @commands.command(
        help="Lyrics quiz on various difficulties of Martin Garrix, Area 21, GRX and YTRAM songs."
    )
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
        end = len(lines) - 1 - difficulty_lines.get(difficulty, 3) // 2
        if difficulty == "extreme":
            start = len(lines) // 2
            end = len(lines) - 1 - difficulty_lines.get(difficulty, 3) // 2
        line_number = random.randint(start, end)
        tries = 0
        while lyrics == "":
            tries += 1
            lyrics = "\n".join(
                lines[line_number: line_number + difficulty_lines.get(difficulty, 3)]
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
    async def quiz_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(
                title="You are currently on cooldown.",
                description=f" This game can only be played once in 10 minutes."
                f"\nTry again in {int(error.retry_after)} seconds",
                color=disnake.Colour.red(),
            )
            return await ctx.send(embed=embed)
        else:
            print(error)

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
                    "Member needs to have atleast 200 Garrix to be robbed."
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
    async def rob_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(
                title="You are currently on cooldown.",
                description=f" Woah theif, you can only rob once in 3 hours.\nTry again "
                f"in {int(error.retry_after)} seconds",
                color=disnake.Colour.red(),
            )
            return await ctx.send(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)
            print(error)

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
        query = "UPDATE users SET in_hand = in_hand + $2, garrix_coins = garrix_coins - $2 WHERE id = $1"
        await self.bot.database.execute(query, ctx.author.id, amt)
        return await ctx.send(
            embed=await success_embed(f"Successfully withdrew {amount} coins.")
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
        query = "UPDATE users SET in_hand = in_hand - $2, garrix_coins = garrix_coins + $2 WHERE id = $1 "
        await self.bot.database.execute(query, ctx.author.id, amt)
        return await ctx.send(
            embed=await success_embed(f"Successfully deposited {amount} coins.")
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
        query = "UPDATE users SET in_hand = in_hand + $2 WHERE id = $1"
        await self.bot.database.execute(query, member.id, amt)
        query = "UPDATE users SET in_hand = in_hand - $2 WHERE id = $1"
        await self.bot.database.execute(query, ctx.author.id, amt)
        return await ctx.send(
            embed=await success_embed(
                f"Successfully gave {amount} coins to {member.display_name}."
            )
        )


def setup(bot):
    bot.add_cog(Fun(bot))
