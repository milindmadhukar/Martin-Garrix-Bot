import traceback

import discord
from discord.ext import commands, tasks
import asyncio
import os

from asyncpg import IntegrityConstraintViolationError

import asyncpraw
from googleapiclient.discovery import build

from core.MartinBotBase import MartinGarrixBot


class Notifications(commands.Cog):
    def __init__(self, bot: MartinGarrixBot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="Martin Garrix Bot",
        )

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "auth.json"
        self.youtube = build(
            "youtube", "v3", developerKey=os.getenv("YOUTUBE_API_TOKEN")
        )

    async def cog_load(self) -> None:
        self.getRedditPosts.start()
        self.getYtVids.start()

    @tasks.loop(minutes=3)
    async def getRedditPosts(self):
        await self.bot.wait_until_ready()
        try:
            subreddit = await self.reddit.subreddit("Martingarrix")
            new_post = subreddit.new(limit=5)
            async for post in new_post:
                await post.load()
                try:
                    await self.bot.database.execute(
                        "INSERT INTO reddit_posts(post_id) VALUES ($1)", post.id
                    )
                except IntegrityConstraintViolationError:
                    continue
                except Exception as e:
                    print(e)
                    return
                    # TODO: Send to error channel

                embed = discord.Embed(
                    title=post.title,
                    url=f"https://reddit.com{post.permalink}",
                    color=discord.Color.orange(),
                )
                if post.selftext:
                    embed.add_field(name="Content", value=post.selftext, inline=False)
                try:
                    if post.preview["images"][0]["source"]["url"]:
                        embed.set_image(url=post.preview["images"][0]["source"]["url"])
                except Exception as error:
                    print(
                        traceback.format_exception(
                            type(error), error, error.__traceback__
                        )
                    )
                    pass

                embed.set_footer(
                    text=f"Author: u/{post.author} on Subreddit {post.subreddit_name_prefixed}"
                )
                reddit_channel = self.bot.reddit_notifications_channel

                await reddit_channel.send(
                    f"{self.bot.reddit_notifications_role.mention} New post on r/Martingarrix",
                    embed=embed,
                )
                await asyncio.sleep(3)
        except Exception as e:
            print(e)

    @tasks.loop(minutes=3)
    async def getYtVids(self):
        await self.bot.wait_until_ready()
        try:
            playlist_ids = [
                "UU5H_KXkPbEsGs0tFt8R35mA",
                "PLwPIORXMGwchuy4DTiIAasWRezahNrbUJ",
            ]
            for playlist_id in playlist_ids:
                video = self.youtube.playlistItems().list(
                    playlistId=playlist_id, part="snippet", maxResults=3
                )
                loop = asyncio.get_event_loop()
                video = await loop.run_in_executor(None, video.execute)
                channel_title = video["items"][0]["snippet"]["channelTitle"]
                video_id = video["items"][0]["snippet"]["resourceId"]["videoId"]
                try:
                    await self.bot.database.execute(
                        "INSERT INTO youtube_videos(video_id) VALUES  ($1)", video_id
                    )
                except IntegrityConstraintViolationError:
                    continue
                except Exception as e:
                    print(e)
                    # TODO: Send to error channel
                    return
                youtube_notification_channel = self.bot.youtube_notifications_channel
                await youtube_notification_channel.send(
                    f"Hey {self.bot.garrix_news_role.mention}, {channel_title} just posted a new video. "
                    f"Go check it out!\nhttps://www.youtube.com/watch?v={video_id}"
                )
                await asyncio.sleep(3)
        except Exception as error:
            print(traceback.format_exception(type(error), error, error.__traceback__))
            pass


async def setup(bot):
    await bot.add_cog(Notifications(bot))

