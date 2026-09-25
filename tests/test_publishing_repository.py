"""
Tests for Shadow Files publication repository.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.publishing.models import (
    Publication,
    PublicationMode,
    PublicationPackage,
)
from app.publishing.repository import PublicationRepository
from app.publishing.status import PublicationStatus


class TestPublicationRepository(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("PRAGMA foreign_keys = ON")

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

        self.repository = PublicationRepository(
            self.connection
        )

        self.now = datetime.now(timezone.utc)

        self.package = PublicationPackage(
            production_id="prod-001",
            video_location="/videos/episode.mp4",
            thumbnail_location="/images/thumbnail.jpg",
            title="Shadow Files Episode",
            description="A completed episode.",
            tags=("true crime", "mystery"),
            category_id="24",
            playlist_id="playlist-001",
        )

        self.publication = Publication(
            publication_id="pub-001",
            production_id="prod-001",
            mode=PublicationMode.HUMAN,
            status=PublicationStatus.NOT_STARTED,
            package=self.package,
            created_at=self.now,
            updated_at=self.now,
        )

    def tearDown(self):
        self.connection.close()

    def test_create_and_get(self):
        created = self.repository.create(
            self.publication
        )

        self.assertEqual(
            created.publication_id,
            "pub-001",
        )

        retrieved = self.repository.get("pub-001")

        self.assertIsNotNone(retrieved)
        self.assertEqual(
            retrieved.publication_id,
            "pub-001",
        )
        self.assertEqual(
            retrieved.production_id,
            "prod-001",
        )
        self.assertEqual(
            retrieved.mode,
            PublicationMode.HUMAN,
        )
        self.assertEqual(
            retrieved.status,
            PublicationStatus.NOT_STARTED,
        )
        self.assertEqual(
            retrieved.package.tags,
            ("true crime", "mystery"),
        )

    def test_get_missing_returns_none(self):
        result = self.repository.get(
            "does-not-exist"
        )

        self.assertIsNone(result)

    def test_list_for_production(self):
        self.repository.create(
            self.publication
        )

        second = Publication(
            publication_id="pub-002",
            production_id="prod-001",
            mode=PublicationMode.YOUTUBE_API,
            status=PublicationStatus.NOT_STARTED,
            package=self.package,
            created_at=self.now,
            updated_at=self.now,
        )

        self.repository.create(second)

        publications = self.repository.list_for_production(
            "prod-001"
        )

        self.assertEqual(len(publications), 2)
        self.assertEqual(
            publications[0].publication_id,
            "pub-001",
        )
        self.assertEqual(
            publications[1].publication_id,
            "pub-002",
        )

    def test_update_status_valid_transition(self):
        self.repository.create(
            self.publication
        )

        updated_at = datetime.now(timezone.utc)

        updated = self.repository.update_status(
            "pub-001",
            PublicationStatus.PACKAGE_READY,
            updated_at,
        )

        self.assertEqual(
            updated.status,
            PublicationStatus.PACKAGE_READY,
        )

        stored = self.repository.get("pub-001")

        self.assertEqual(
            stored.status,
            PublicationStatus.PACKAGE_READY,
        )

    def test_update_status_invalid_transition_rejected(self):
        self.repository.create(
            self.publication
        )

        with self.assertRaises(ValueError):
            self.repository.update_status(
                "pub-001",
                PublicationStatus.PUBLISHED,
                datetime.now(timezone.utc),
            )

    def test_update_status_missing_publication_rejected(self):
        with self.assertRaises(ValueError):
            self.repository.update_status(
                "missing",
                PublicationStatus.PACKAGE_READY,
                datetime.now(timezone.utc),
            )

    def test_update_metadata(self):
        self.repository.create(
            self.publication
        )

        uploaded_at = datetime.now(timezone.utc)

        updated = self.repository.update_metadata(
            "pub-001",
            uploaded_at=uploaded_at,
            youtube_video_id="youtube-123",
            youtube_url="https://youtube.example/video",
            updated_at=uploaded_at,
        )

        self.assertEqual(
            updated.youtube_video_id,
            "youtube-123",
        )
        self.assertEqual(
            updated.youtube_url,
            "https://youtube.example/video",
        )
        self.assertEqual(
            updated.uploaded_at,
            uploaded_at,
        )

    def test_update_metadata_requires_timezone_aware_timestamp(self):
        self.repository.create(
            self.publication
        )

        with self.assertRaises(ValueError):
            self.repository.update_metadata(
                "pub-001",
                updated_at=datetime.now(),
            )

    def test_foreign_key_requires_existing_production(self):
        invalid_package = PublicationPackage(
            production_id="missing-production",
            video_location="/videos/episode.mp4",
            thumbnail_location="/images/thumbnail.jpg",
            title="Episode",
            description="Description",
        )

        invalid_publication = Publication(
            publication_id="pub-invalid",
            production_id="missing-production",
            mode=PublicationMode.HUMAN,
            status=PublicationStatus.NOT_STARTED,
            package=invalid_package,
            created_at=self.now,
            updated_at=self.now,
        )

        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.create(
                invalid_publication
            )


if __name__ == "__main__":
    unittest.main()
