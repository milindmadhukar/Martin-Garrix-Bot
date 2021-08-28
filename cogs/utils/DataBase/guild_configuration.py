import discord


class GuildConfig(object):
    def __init__(self, bot,
                 guild_id: int,
                 xp_multiplier: int = 1,
                 muted_role: int = None,
                 modlogs_channel: int = None,
                 leave_join_logs_channel: int = None,
                 reddit_notifications_channel: int = None,
                 youtube_notifications_channel: int = None,
                 welcomes_channel: int = None,
                 edit_logs_channel: int = None,
                 delete_logs_channel: int = None,
                 *args, **kwargs):
        self.bot = bot
        self.guild_id = guild_id
        self.xp_multiplier = xp_multiplier
        self.muted_role = muted_role
        self.modlogs_channel = modlogs_channel
        self.leave_join_logs_channel = leave_join_logs_channel
        self.reddit_notifications_channel = reddit_notifications_channel
        self.youtube_notifications_channel = youtube_notifications_channel
        self.welcomes_channel = welcomes_channel
        self.edit_logs_channel = edit_logs_channel
        self.delete_logs_channel = delete_logs_channel

    async def post(self):
        query = """INSERT INTO guild_configs ( guild_id)
                           VALUES ( $1 ) ON CONFLICT DO NOTHING"""
        await self.bot.db.execute(query, self.guild_id)

    @classmethod
    async def on_guild_channel_delete(cls, bot, channel: discord.TextChannel):
        guild = await bot.db.get_guild_config(guild_id=channel.guild.id)
        guild_attrs = vars(guild)
        for attr in guild_attrs.keys():
            if guild_attrs[attr] == channel.id:
                query = f"""UPDATE guild_configs SET {attr} = NULL WHERE guild_id = $1 """
                await bot.db.execute(query, guild.guild_id)

    @classmethod
    async def on_guild_role_delete(cls, bot, role: discord.Role):
        guild = await bot.db.get_guild_config(guild_id=role.guild.id)
        guild_attrs = vars(guild)
        for attr in guild_attrs.keys():
            if guild_attrs[attr] == role.id:
                query = f"""UPDATE guild_configs SET {attr} = NULL WHERE guild_id = $1 """
                await bot.db.execute(query, guild.guild_id)

    @classmethod
    async def init_guild(cls, bot, guild_id):
        self = GuildConfig(bot=bot, guild_id=guild_id)
        await self.post()

    async def update_muted_role(self, muted_role):
        self.muted_role = muted_role
        query = """UPDATE guild_configs SET muted_role = $1 WHERE guild_id = $2"""
        await self.bot.db.execute(query, self.muted_role, self.guild_id)

    async def update_modlogs_channel(self, modlogs_channel):
        self.modlogs_channel = modlogs_channel
        query = """UPDATE guild_configs SET modlogs_channel = $1 WHERE guild_id = $2"""
        await self.bot.db.execute(query, self.modlogs_channel, self.guild_id)

    async def update_leave_join_logs_channel(self, leave_join_logs_channel):
        self.leave_join_logs_channel = leave_join_logs_channel
        query = """UPDATE guild_configs SET leave_join_logs_channel = $1 WHERE guild_id = $2"""
        await self.bot.db.execute(query, self.leave_join_logs_channel, self.guild_id)

    async def update_youtube_notifications_channel(self, youtube_notifications_channel):
        self.youtube_notifications_channel = youtube_notifications_channel
        query = """UPDATE guild_configs SET youtube_notifications_channel = $1 WHERE guild_id = $2"""
        await self.bot.db.execute(query, self.youtube_notifications_channel, self.guild_id)

    async def update_reddit_notifications_channel(self, reddit_notifications_channel):
        self.reddit_notifications_channel = reddit_notifications_channel
        query = """UPDATE guild_configs SET reddit_notifications_channel = $1 WHERE guild_id = $2"""
        await self.bot.db.execute(query, self.reddit_notifications_channel, self.guild_id)

    async def update_welcomes_channel(self, welcomes_channel):
        self.welcomes_channel = welcomes_channel
        query = """UPDATE guild_configs SET welcomes_channel = $1 WHERE guild_id = $2"""
        await self.bot.db.execute(query, self.welcomes_channel, self.guild_id)

    async def update_edit_logs_channel(self, edit_logs_channel):
        self.edit_logs_channel = edit_logs_channel
        query = """UPDATE guild_configs SET edit_logs_channel = $1 WHERE guild_id = $2"""
        await self.bot.db.execute(query, self.edit_logs_channel, self.guild_id)

    async def update_delete_logs_channel(self, delete_logs_channel):
        self.delete_logs_channel = delete_logs_channel
        query = """UPDATE guild_configs SET delete_logs_channel = $1 WHERE guild_id = $2"""
        await self.bot.db.execute(query, self.delete_logs_channel, self.guild_id)

    async def update_xp_multiplier(self, xp_multiplier):
        self.xp_multiplier = xp_multiplier
        query = """UPDATE guild_configs SET xp_multiplier = $1 WHERE guild_id = $2"""
        await self.bot.db.execute(query, self.xp_multiplier, self.guild_id)

class Guild:
    def __init__(self, bot, guild_id: int, name: str, owner_id: int):
        self.bot = bot
        self.guild_id = guild_id
        self.name = name
        self.owner_id = owner_id

    async def post(self):
        query = """INSERT INTO guilds (id, name, owner_id)
                                   VALUES ( $1, $2, $3) ON CONFLICT DO NOTHING"""
        await self.bot.db.execute(query, self.guild_id, self.name, self.owner_id)

    @classmethod
    async def init_guild(cls, bot, guild_id: int, name: str, owner_id: int):
        self = Guild(bot=bot, guild_id=guild_id, name=name, owner_id=owner_id)
        await self.post()
