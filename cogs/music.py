import os
import wavelink
from discord.ext import commands
import discord
from utils.checks import is_milind_check
from utils.helpers import success_embed

# TODO: vote to skip


class Music(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vc = None
        self.skippers = set()

        bot.loop.create_task(self.connect_nodes())


    @commands.Cog.listener()
    async def on_voice_server_update(self, member, before, after):
        if member.bot:
            return

        if member not in after.channel.members:
            self.skippers.discard(member)

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        """Connect to our Lavalink nodes."""

        node = wavelink.Node(uri=f"http://{os.getenv('LAVALINK_HOST')}:{os.getenv('LAVALINK_PORT')}", password=os.getenv('LAVALINK_PASSWORD'))

        await wavelink.NodePool.connect(client=self.bot, nodes=[node])




    async def get_random_song(self):
        song_name = await self.bot.database.fetchrow(
            "SELECT alias, name FROM songs ORDER BY RANDOM() LIMIT 1"
        )
        if song_name is None:
            return
        alias = song_name.get("alias", "Martin Garrix")
        name = song_name.get("name", "High On Life")
        return alias, name

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f"Node: <{node.id}> is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, *args, **kwargs):
        alias, name = await self.get_random_song()
        song_name = f"{alias} - {name}"

        track = await wavelink.YouTubeTrack.search(song_name)

        await self.vc.play(track[0])

        if len(song_name) >= 16:
            song_name = name
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, name=song_name
            )
        )

    async def play_random_song(self):
        alias, name = await self.get_random_song()
        song_name = f"{alias} - {name}"

        track = await wavelink.YouTubeTrack.search(song_name)

        await self.vc.play(track[0])

        if len(song_name) >= 16:
            song_name = name
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, name=song_name
            )
        )

    @commands.command()
    @is_milind_check()
    async def startradio(self, ctx: commands.Context):
        """Play a song with the given search query.

        If not connected, connect to our voice channel.
        """
        if not ctx.voice_client:
            self.vc: wavelink.Player = await ctx.author.voice.channel.connect(
                cls=wavelink.Player
            )
        else:
            self.vc: wavelink.Player = ctx.voice_client

        await self.play_random_song()

        await ctx.send(embed=await success_embed("Started the radio."))

    @commands.hybrid_command(
        name="skip",
        help="Skip the current song.",
    )
    async def voteskip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel.")
        if not ctx.voice_client.is_playing():
            return await ctx.send("I am not playing anything.")

        if ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.send("You are not in my voice channel.")

        # Get members in the voice channel
        members = [
            member for member in ctx.voice_client.channel.members if not member.bot
        ]
        # add member to skippers
        self.skippers.add(ctx.author)

        await ctx.send(
            f"({len(self.skippers)}/{len(members)//2 or 1}) {ctx.author.mention} has voted to skip the song."
        )

        # if more than half of the members in the voice channel have voted to skippers
        if len(self.skippers) >= len(members) // 2:
            # end the song
            await ctx.voice_client.stop()

            return await ctx.send("Skipped the song.")

    @is_milind_check()
    async def force_skip(self):
        if not self.vc.is_playing():
            return
        await self.vc.stop()


async def setup(bot):
    await bot.add_cog(Music(bot))
