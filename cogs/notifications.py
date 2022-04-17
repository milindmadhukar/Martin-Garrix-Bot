import discord
from discord.ext import commands, tasks
import asyncio
import os

from .  utils.notification import latestYtVid
import asyncpraw
from googleapiclient.discovery import build

class Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
                                       client_secret=os.getenv('REDDIT_CLIENT_SECRET'), user_agent="Martin Garrix Bot")

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "auth.json"
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_TOKEN'))
        self.getRedditPosts.start()
        self.getYtVids.start()

    @tasks.loop(minutes=3)
    async def getRedditPosts(self):
        try:
            subreddit = await self.reddit.subreddit('Martingarrix')
            new_post = subreddit.new(limit=5)
            async for post in new_post:
                try:
                    await self.bot.db.execute("INSERT INTO reddit_posts(post_id) VALUES ($1)", post.id)
                except:
                    continue
                embed = discord.Embed(title=post.title,
                                      url=f"https://reddit.com{post.permalink}",
                                      color=discord.Color.orange())
                if post.selftext:
                    embed.add_field(name="Content", value=post.selftext, inline=False)
                try:
                    if post.preview['images'][0]['source']['url']:
                        embed.set_image(url=post.preview['images'][0]['source']['url'])
                except:
                    pass

                embed.set_footer(
                    text=f"Author: u/{post.author} on Subreddit {post.subreddit_name_prefixed}")
                reddit_channel = self.bot.reddit_notifications_channel

                return await reddit_channel.send(embed=embed)
        except:
            pass



    @tasks.loop(minutes=3)
    async def getYtVids(self):
        try:
            playlist_ids = ['UU5H_KXkPbEsGs0tFt8R35mA', 'PLwPIORXMGwchuy4DTiIAasWRezahNrbUJ']
            for playlist_id in playlist_ids:
                video = self.youtube.playlistItems().list(playlistId=playlist_id, part="snippet", maxResults=1)
                loop = asyncio.get_event_loop()
                video = await loop.run_in_executor(None, video.execute)
                video_id = video['items'][0]['snippet']['resourceId']['videoId']
                try:
                    await self.bot.db.execute("INSERT INTO youtube_videos(video_id) VALUES  ($1)", video_id)
                except:
                    continue
                youtube_notification_channel = self.bot.youtube_notifications_channel
                try:
                    await youtube_notification_channel.send('https://www.youtube.com/watch?v=' + video_id)
                except:
                    pass
        except:
            pass


def setup(bot):
    bot.add_cog(Notifications(bot))
