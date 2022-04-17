import discord
from discord.ext import commands
import random
import asyncio
from difflib import SequenceMatcher

from .utils.custom_embed import failure_embed

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help="Get the lyrics of any Martin Garrix, Area 21, GRX or YTRAM song.")
    async def lyrics(self, ctx, *, song_name):
        query = "SELECT * FROM songs WHERE name LIKE $1"
        song_data = await self.bot.db.fetchrow(query, song_name)

        if song_data is None:
            return await ctx.send(embed= await failure_embed(title="No such song found."))

        embed = discord.Embed(title =f'{song_data["alias"]} - {song_data["name"]}',
                              description = song_data['lyrics'][:4096],
                              color=discord.Colour.orange())

        if song_data['thumbnail_url'] is not None:
            embed.set_thumbnail(url=song_data['thumbnail_url'])

        return await ctx.send(embed=embed)


    @commands.command(help="Lyrics quiz on various difficulties of Martin Garrix, Area 21, GRX and YTRAM songs.")
    @commands.cooldown(1, 3*60 , commands.BucketType.user)
    async def quiz(self, ctx, difficulty: lambda inp: inp.lower()=None):
        if difficulty == None or difficulty not in ['easy', 'medium', 'hard', 'extreme']:
            embed = discord.Embed(title="Please choose an appropriate difficulty level.", description="Your choices are:\n**easy** : 50 garrix coins\n**medium** : 100 garrix coins\n**hard** : 150 garrix coins\n**extreme** : 200 garrix coins", color=discord.Colour.teal())
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=embed)

        query = "SELECT * FROM songs WHERE lyrics IS NOT NULL ORDER BY RANDOM() LIMIT 1"
        if difficulty == 'easy':
            query = query[:44] + " AND alias = 'Martin Garrix'" + query[44:]
        song = await self.bot.db.fetchrow(query)
        lines = song['lyrics'].split('\n')
        lyrics = ""
        difficulty_lines = {'easy' : 3, 'medium' : 2, 'hard' : 1, 'extreme' : 1}
        start = 0
        end = len(lines) - 1 - difficulty_lines.get(difficulty, 3) // 2
        if difficulty == 'extreme':
            start = len(lines) // 2
            end = len(lines) - 1 - difficulty_lines.get(difficulty, 3) // 2
        line_number = random.randint(start, end)

        while lyrics == "":
            lyrics = "\n".join(lines[line_number:line_number + difficulty_lines.get(difficulty, 3)])

        embed = discord.Embed(title=f"Guess the song from the lyrics! ({difficulty.title()})", description="Guess the song name within 45 seconds.", colour=discord.Colour.gold())
        embed.add_field(name="Lyrics", value=lyrics)
        embed.set_footer(text=f"Game for {ctx.author.name}")

        await ctx.send(embed=embed)

        check = lambda m: (m.author.id == ctx.author.id and m.channel.id == ctx.channel.id)

        embed = None
        guess = None
        similarity = None

        try:
            guess = await self.bot.wait_for('message', check=check, timeout=30)
            similarity = SequenceMatcher(None, song['name'].lower().replace(" ", ""), guess.content.lower().replace(" ", "")).ratio()

        except asyncio.TimeoutError:
            embed = await failure_embed("Oops, you ran out of time")

        if similarity is not None:
            if similarity > 0.7:
                earning_dict = {'easy' : 50 , 'medium' : 100, 'hard' : 150, 'extreme' : 200}
                earning = earning_dict.get(difficulty)
                embed = discord.Embed(title=f"<a:tick:810462879374770186> Your guess is correct and you earned {earning} Garrix Coins.", colour=discord.Colour.green())
                user = await self.bot.db.get_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
                user.garrix_coins += earning
                await user.update_garrix_coins()

            else:
                embed = discord.Embed(title=f"<a:cross:810462920810561556>  Your guess is incorrect", colour=discord.Colour.red())
        
        embed.add_field(name="Song Name", value=f"{song['alias']} - {song['name']}")
        if song['thumbnail_url'] is not None:
            embed.set_thumbnail(url = song['thumbnail_url'])

        try:
            await ctx.send(embed=embed)
        except:
            ctx.command.reset_cooldown(ctx)
            return await ctx.senc("Some error occurred, please try again.")

    @quiz.error
    async def quiz_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(title="You are currently on cooldown.", description=f" This game can only be played once in 10 minutes.\nTry again in {int(error.retry_after)} seconds", color=discord.Colour.red())

            return await ctx.send(embed=embed)

    @commands.command(help="Check you account balance for Garrix coins", aliases=['bal'])
    async def balance(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        query = "SELECT in_hand, garrix_coins FROM users WHERE id = $1 AND guild_id = $2"
        record = await self.bot.db.fetchrow(query, ctx.author.id, ctx.guild.id)
        in_hand = record["in_hand"]
        garrix_coins = record["garrix_coins"]
        embed = discord.Embed(title="Garrix Bank", colour=discord.Colour.orange())
        embed.add_field(name="In hand", value=in_hand, inline=True)
        embed.add_field(name="In Garrix Bank", value=garrix_coins, inline=True)
        embed.set_thumbnail(url=member.avatar_url_as(size=256))
        # embed.set_footer(f"Balance of {member.name}")

        return await ctx.send(embed=embed)




    
def setup(bot):
    bot.add_cog(Fun(bot))
