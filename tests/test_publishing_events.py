"""
Tests for Shadow Files publication event persistence.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.publishing.events import PublicationEventRepository
from database.publishing_schema import CREATE_PUBLISHING_SCHEMA_SQL


class TestPublicationEventRepository(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")

        self.connection.execute(
            """
            CREATE TABLE productions (
                production_id TEXT PRIMARY KEY
            )
            """
        )

        self.connection.execute(
            """
            INSERT INTO productions (production_id)
            VALUES ('prod-001')
            """
        )

        self.connection.execute(
            """
            CREATE TABLE publications (
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
            )
            """
        )

        self.connection.execute(
            """
            INSERT INTO publications (
                publication_id,
                production_id,
                mode,
                status,
                video_location,
                thumbnail_location,
                title,
                description,
                tags_json,
                created_at,
                updated_at
            )
            VALUES (
                'pub-001',
                'prod-001',
                'HUMAN',
                'NOT_STARTED',
                '/video.mp4',
                '/thumbnail.jpg',
                'Episode',
                'Description',
                '[]',
                ?,
                ?
            )
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        self.connection.executescript(
            CREATE_PUBLISHING_SCHEMA_SQL.split(
                "CREATE TABLE IF NOT EXISTS publications"
            )[1].split(
                "CREATE INDEX IF NOT EXISTS idx_publications_production"
            )[0]
            if False
            else """
            CREATE TABLE publication_events (
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

            CREATE INDEX idx_publication_events_publication
                ON publication_events(publication_id);

            CREATE INDEX idx_publication_events_created
                ON publication_events(created_at);
            """
        )

        self.repository = PublicationEventRepository(
            self.connection
        )

    def tearDown(self):
        self.connection.close()

    def test_record_event(self):
        now = datetime.now(timezone.utc)

        event = self.repository.record(
            publication_id="pub-001",
            event_type="PUBLICATION_CREATED",
            status="NOT_STARTED",
            actor="system",
            details="Publication created.",
            created_at=now,
        )

        self.assertEqual(
            event.publication_id,
            "pub-001",
        )
        self.assertEqual(
            event.event_type,
            "PUBLICATION_CREATED",
        )
        self.assertEqual(
            event.status,
            "NOT_STARTED",
        )
        self.assertEqual(
            event.actor,
            "system",
        )

    def test_list_events(self):
        first_time = datetime.now(timezone.utc)

        self.repository.record(
            publication_id="pub-001",
            event_type="PUBLICATION_CREATED",
            status="NOT_STARTED",
            actor="system",
            created_at=first_time,
        )

        second_time = datetime.now(timezone.utc)

        self.repository.record(
            publication_id="pub-001",
            event_type="PACKAGE_READY",
            status="PACKAGE_READY",
            actor="system",
            created_at=second_time,
        )

        events = self.repository.list_for_publication(
            "pub-001"
        )

        self.assertEqual(len(events), 2)
        self.assertEqual(
            events[0].event_type,
            "PUBLICATION_CREATED",
        )
        self.assertEqual(
            events[1].event_type,
            "PACKAGE_READY",
        )

    def test_events_are_append_only_through_repository_api(self):
        self.repository.record(
            publication_id="pub-001",
            event_type="PUBLICATION_CREATED",
        )

        self.repository.record(
            publication_id="pub-001",
            event_type="PACKAGE_READY",
        )

        events = self.repository.list_for_publication(
            "pub-001"
        )

        self.assertEqual(len(events), 2)


if __name__ == "__main__":
    unittest.main()
