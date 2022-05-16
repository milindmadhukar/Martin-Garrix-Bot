CREATE TABLE IF NOT EXISTS modlogs(
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    log_type VARCHAR(20) NOT NULL,
    reason VARCHAR(400),
    "time" timestamp without time zone DEFAULT (now())::timestamp without time zone
);

CREATE TABLE IF NOT EXISTS join_leave_logs (
    member_id BIGINT NOT NULL,
    action VARCHAR(5) NOT NULL,
    "time" timestamp without time zone DEFAULT (now())::timestamp without time zone,
    CONSTRAINT action_constraint CHECK (((action)::text = ANY (ARRAY[('join'::character varying)::text, ('leave'::character varying)::text])))
);


CREATE TABLE IF NOT EXISTS messages (
    message_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    author_id bigint NOT NULL,
    content character varying(2050) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT (now())::timestamp without time zone
);

CREATE TABLE IF NOT EXISTS tags (
    creator_id bigint NOT NULL,
    content character varying(2050) NOT NULL,
    created_at timestamp without time zone DEFAULT (now())::timestamp without time zone,
    uses integer DEFAULT 0,
    name character varying(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id bigint NOT NULL UNIQUE,
    messages_sent integer DEFAULT 0,
    total_xp integer DEFAULT 0,
    last_xp_added timestamp without time zone,
    garrix_coins bigint DEFAULT 0,
    in_hand bigint DEFAULT 0
);

CREATE TABLE IF NOT EXISTS songs(
    alias VARCHAR(100),
    name VARCHAR(100) UNIQUE NOT NULL,
    lyrics text,
    thumbnail_url text
);

CREATE TABLE IF NOT EXISTS reddit_posts(
    post_id VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS youtube_videos(
    video_id VARCHAR(100) UNIQUE NOT NULL
);