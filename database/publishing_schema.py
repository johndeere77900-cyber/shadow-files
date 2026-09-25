"""
Database schema for Shadow Files publication records.
"""

SCHEMA_VERSION = 1


CREATE_PUBLISHING_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS publications (
    publication_id TEXT PRIMARY KEY,
    production_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,

    video_location TEXT NOT NULL,
    thumbnail_location TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    tags_json TEXT NOT NULL DEFAULT '[]',
    category_id TEXT,
    playlist_id TEXT,
    disclosure TEXT,

    approved_at TEXT,
    uploaded_at TEXT,
    scheduled_at TEXT,
    published_at TEXT,

    youtube_video_id TEXT,
    youtube_url TEXT,
    error_message TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (production_id)
        REFERENCES productions(production_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_publications_production
    ON publications(production_id);

CREATE INDEX IF NOT EXISTS idx_publications_status
    ON publications(status);

CREATE INDEX IF NOT EXISTS idx_publications_mode
    ON publications(mode);

CREATE TABLE IF NOT EXISTS publication_events (
    event_id TEXT PRIMARY KEY,
    publication_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT,
    actor TEXT,
    details TEXT,
    created_at TEXT NOT NULL,

    FOREIGN KEY (publication_id)
        REFERENCES publications(publication_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_publication_events_publication
    ON publication_events(publication_id);

CREATE INDEX IF NOT EXISTS idx_publication_events_created
    ON publication_events(created_at);
"""


def get_publishing_schema_sql() -> str:
    """Return the SQL required to create the publishing schema."""

    return CREATE_PUBLISHING_SCHEMA_SQL
