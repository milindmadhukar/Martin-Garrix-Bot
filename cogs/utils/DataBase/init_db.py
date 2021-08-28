guild_configs = """CREATE TABLE IF NOT EXISTS guild_configs(
    guild_id BIGINT NOT NULL UNIQUE,
    xp_multiplier INTEGER DEFAULT 1,
    muted_role BIGINT,
    modlogs_channel BIGINT,
    leave_join_logs_channel BIGINT,
    reddit_notifications_channel BIGINT,
    youtube_notifications_channel BIGINT,
    welcomes_channel BIGINT,
    edit_logs_channel BIGINT,
    delete_logs_channel BIGINT,
    xp_disabled_channels BIGINT[]
)"""

guilds = """CREATE TABLE IF NOT EXISTS guilds (
    id BIGINT NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    owner_id BIGINT NOT NULL
)"""

modlogs = """CREATE TABLE IF NOT EXISTS modlogs(
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    log_type VARCHAR(20) NOT NULL,
    reason VARCHAR(400),
    "time" timestamp without time zone DEFAULT (now())::timestamp without time zone
)"""

leave_join_logs = """CREATE TABLE IF NOT EXISTS join_leave_logs (
    guild_id BIGINT NOT NULL,
    member_id BIGINT NOT NULL,
    action VARCHAR(5) NOT NULL,
    "time" timestamp without time zone DEFAULT (now())::timestamp without time zone,
    CONSTRAINT action_constraint CHECK (((action)::text = ANY (ARRAY[('join'::character varying)::text, ('leave'::character varying)::text])))
)
"""

messages = """CREATE TABLE IF NOT EXISTS messages (
    message_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    guild_id bigint NOT NULL,
    author_id bigint NOT NULL,
    content character varying(2050) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT (now())::timestamp without time zone
)"""

tags = """CREATE TABLE IF NOT EXISTS tags (
    guild_id bigint NOT NULL,
    creator_id bigint NOT NULL,
    content character varying(2050) NOT NULL,
    created_at timestamp without time zone DEFAULT (now())::timestamp without time zone,
    uses integer DEFAULT 0,
    name character varying(200) NOT NULL
)"""

users = """CREATE TABLE IF NOT EXISTS users (
    id bigint NOT NULL,
    guild_id bigint NOT NULL,
    messages_sent integer DEFAULT 0,
    total_xp integer DEFAULT 0,
    last_xp_added timestamp without time zone,
    garrix_coins bigint DEFAULT 0,
    CONSTRAINT unique_user UNIQUE(id, guild_id)
)"""

songs = """CREATE TABLE IF NOT EXISTS songs(
    alias VARCHAR(100),
    name VARCHAR(100) UNIQUE NOT NULL,
    lyrics text,
    thumbnail_url text
)"""

reddit_posts = """CREATE TABLE IF NOT EXISTS reddit_posts(
    post_id VARCHAR(100) UNIQUE NOT NULL
)"""

youtube_videos = """CREATE TABLE IF NOT EXISTS youtube_videos(
    video_id VARCHAR(100) UNIQUE NOT NULL
)"""

timed_events = """CREATE TABLE IF NOT EXISTS timed_events(
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100),
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    end_time timestamp without time zone,
    CONSTRAINT unique_event UNIQUE (event_type, user_id, guild_id)
)"""

custom_roles = """CREATE TABLE IF NOT EXISTS custom_roles(
    member_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    CONSTRAINT unique_role UNIQUE (member_id, guild_id)
)"""

a_reaction_roles = """CREATE TABLE IF NOT EXISTS reaction_roles(
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL
)"""

emoji_role = """CREATE TABLE IF NOT EXISTS emoji_role(
    id SERIAL PRIMARY KEY,
    emoji VARCHAR(500) NOT NULL,
    role_id BIGINT NOT NULL,
    reaction_role_id INTEGER REFERENCES reaction_roles (id) ON DELETE CASCADE,
    CONSTRAINT unique_emoji_roles UNIQUE (emoji, role_id)
)"""
