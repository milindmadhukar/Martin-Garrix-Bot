import os
import wavelink
from disnake.ext import commands
import disnake
from utils.checks import is_milind_check
from utils.helpers import success_embed


class Music(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vc = None

        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        """Connect to our Lavalink nodes."""

        await wavelink.NodePool.create_node(
            bot=self.bot,
            host=os.getenv("LAVALINK_HOST"),
            port=int(os.getenv("LAVALINK_PORT")),
            password=os.getenv("LAVALINK_PASSWORD"),
            https=True,
        )

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
        print(f"Node: <{node.identifier}> is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, *args, **kwargs):
        alias, name = await self.get_random_song()
        song_name = f"{alias} - {name}"

        track = await wavelink.YouTubeTrack.search(query=song_name, return_first=True)

        await self.vc.play(track)

        if len(song_name) >= 16:
            song_name = name
        await self.bot.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.listening, name=song_name
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

        alias, name = await self.get_random_song()
        song_name = f"{alias} - {name}"

        track = await wavelink.YouTubeTrack.search(query=song_name, return_first=True)

        await self.vc.play(track)

        if len(song_name) >= 16:
            song_name = name
        await self.bot.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.listening, name=song_name
            )
        )

        await ctx.send(embed=await success_embed("Started the radio."))

def setup(bot):
    bot.add_cog(Music(bot))
