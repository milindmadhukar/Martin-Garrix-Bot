from enum import Enum

__all__ = ("Config",)


class Config(Enum):
    """
    This class is an :class:`Enum` that contains configuration data for the bot to use.
    """

    GUILD_ID = 1234
    MODLOGS_CHANNEL = 1234  # Optional
    LEAVE_JOIN_LOGS_CHANNEL = 1234  # Optional
    YOUTUBE_NOTIFICATION_CHANNEL = 1234  # Optional
    REDDIT_NOTIFICATION_CHANNEL = 1234  # Optional
    WELCOMES_CHANNEL = 1234  # Optional
    DELETE_LOGS_CHANNEL = 1234  # Optional
    EDIT_LOGS_CHANNEL = 1234  # Optional
    XP_MULTIPLIER = 1
    TEAM_ROLE = 1234
    MODERATOR_ROLE = 1234
    ADMIN_ROLE = 1234
    SUPPORT_ROLE = 1234
    GARRXIER_ROLE = 1234
    TRUE_GARRIXER_ROLE = 1234
    REDDIT_NOTIFICATION_ROLE = 1234
    GARRIX_NEWS_ROLE = 1234