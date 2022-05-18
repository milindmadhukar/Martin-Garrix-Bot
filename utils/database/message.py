import datetime
import random

import disnake

__all__ = ("Message",)

from disnake.ext import commands

import utils.helpers as helpers

class Message:
    def __init__(
        self,
        bot: commands.Bot,
        message_id: int,
        channel_id: int,
        author_id: int,
        content: str,
        xp_multiplier: int,
        *args,
        **kwargs,
    ):
        self.bot = bot
        self.message_id = message_id
        self.channel_id = channel_id
        self.author_id = author_id
        self.xp_multiplier = xp_multiplier
        self.content = content

    async def post(self) -> None:
        query = """INSERT INTO messages ( message_id, channel_id, author_id, content)
                   VALUES ( $1, $2, $3, $4 )
                   ON CONFLICT DO NOTHING"""
        await self.bot.database.execute(
            query, self.message_id, self.channel_id, self.author_id, self.content
        )
        return

    @classmethod
    async def on_message(
        cls, bot: commands.Bot, message: disnake.Message, xp_multiplier: int
    ) -> None:
        print(f"{message.author} : {message.content}")
        self = cls(
            bot=bot,
            content=message.content,
            message_id=message.id,
            channel_id=message.channel.id,
            author_id=message.author.id,
            xp_multiplier=xp_multiplier,
        )
        await self.post()
        if message.author.bot:
            return
        user = await bot.database.get_user(message.author.id)
        xp = random.randint(15, 25)
        now = datetime.datetime.now()
        difference = datetime.timedelta(seconds=0)
        if user.last_xp_added is not None:
            difference = now - user.last_xp_added
        if difference > datetime.timedelta(minutes=1) or user.last_xp_added is None:
            before_message_level = helpers.get_user_level(user.total_xp)
            xp_for_next_level = helpers.f_xp_for_next_level(before_message_level)
            user.total_xp += xp * self.xp_multiplier
            user.last_xp_added = now
            await bot.database.execute(
                "UPDATE users SET total_xp = $1, last_xp_added = $2 WHERE id = $3",
                user.total_xp,
                user.last_xp_added,
                user.id,
            )
            if user.total_xp > xp_for_next_level:
                msg = f"GG {message.author}, you just reached level {before_message_level + 1}! <:garrix_pog:976430496965869568> "
                if before_message_level + 1 == bot.true_garrixer_level and bot.true_garrixer_role not in message.author.roles:
                    msg += f"\nCongrats on reaching level {bot.true_garrixer_level}. You have been given the True Garrixer role. <:garrix_wink:811961920977764362>"
                    await message.author.add_roles(bot.true_garrixer_role, reason=f"Reached level {bot.true_garrixer_level}")
                await bot.bots_channel.send(msg)
                    

        await bot.database.execute(
            "UPDATE users SET messages_sent = messages_sent + 1 WHERE id = $1", user.id
        )
        return
