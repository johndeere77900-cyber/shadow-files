"""
Phase 15 integration tests.

Validates the complete publication lifecycle across:
- publication models
- repository
- events
- approval
- service
- YouTube publisher abstraction
"""

import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.publishing.errors import UploadError
from app.publishing.events import PublicationEventRepository
from app.publishing.models import (
    PublicationMode,
    PublicationPackage,
)
from app.publishing.repository import PublicationRepository
from app.publishing.service import PublicationService
from app.publishing.status import PublicationStatus
from app.publishing.youtube import (
    YouTubeUploadRequest,
    YouTubeUploadResult,
)


class FakeYouTubePublisher:
    """Successful fake publisher for integration tests."""

    def upload(
        self,
        request: YouTubeUploadRequest,
    ) -> YouTubeUploadResult:
        uploaded_at = datetime.now(timezone.utc)

        return YouTubeUploadResult(
            success=True,
            video_id="youtube-test-001",
            video_url="https://youtube.example/watch?v=youtube-test-001",
            uploaded_at=uploaded_at,
        )


class FailingYouTubePublisher:
    """Failing fake publisher for failure-path testing."""

    def upload(
        self,
        request: YouTubeUploadRequest,
    ) -> YouTubeUploadResult:
        return YouTubeUploadResult(
            success=False,
            error_message="Simulated upload failure.",
        )


class TestPhase15Integration(unittest.TestCase):
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

        self.connection.execute(
            """
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
            )
            """
        )

        self.repository = PublicationRepository(
            self.connection
        )

        self.event_repository = PublicationEventRepository(
            self.connection
        )

        self.temp_dir = tempfile.TemporaryDirectory()

        self.video_path = Path(
            self.temp_dir.name
        ) / "episode.mp4"

        self.thumbnail_path = Path(
            self.temp_dir.name
        ) / "thumbnail.jpg"

        self.video_path.write_bytes(
            b"test-video"
        )

        self.thumbnail_path.write_bytes(
            b"test-thumbnail"
        )

        self.package = PublicationPackage(
            production_id="prod-001",
            video_location=str(self.video_path),
            thumbnail_location=str(self.thumbnail_path),
            title="Shadow Files — Test Episode",
            description="Integration test publication.",
            tags=(
                "shadow files",
                "true crime",
                "mystery",
            ),
            category_id="24",
        )

    def tearDown(self):
        self.temp_dir.cleanup()
        self.connection.close()

    def test_complete_human_publication_lifecycle(self):
        service = PublicationService(
            repository=self.repository,
            event_repository=self.event_repository,
        )

        publication = service.create_publication(
            production_id="prod-001",
            package=self.package,
            mode=PublicationMode.HUMAN,
        )

        publication_id = publication.publication_id

        self.assertEqual(
            publication.status,
            PublicationStatus.NOT_STARTED,
        )

        publication = service.prepare_package(
            publication_id
        )

        self.assertEqual(
            publication.status,
            PublicationStatus.PACKAGE_READY,
        )

        publication = service.request_approval(
            publication_id
        )

        self.assertEqual(
            publication.status,
            PublicationStatus.PENDING_APPROVAL,
        )

        publication = service.approve(
            publication_id,
            approved_by="boss",
            note="Human approval granted.",
        )

        self.assertEqual(
            publication.status,
            PublicationStatus.APPROVED,
        )

        self.assertIsNotNone(
            publication.approved_at
        )

        uploaded_at = datetime.now(
            timezone.utc
        )

        publication = service.mark_human_uploaded(
            publication_id,
            youtube_video_id="human-video-001",
            youtube_url="https://youtube.example/human-video-001",
            uploaded_at=uploaded_at,
        )

        self.assertEqual(
            publication.status,
            PublicationStatus.UPLOADED,
        )

        self.assertEqual(
            publication.youtube_video_id,
            "human-video-001",
        )

        scheduled_at = datetime.now(
            timezone.utc
        ) + timedelta(days=1)

        publication = service.mark_scheduled(
            publication_id,
            scheduled_at,
        )

        self.assertEqual(
            publication.status,
            PublicationStatus.SCHEDULED,
        )

        self.assertEqual(
            publication.scheduled_at,
            scheduled_at,
        )

        published_at = scheduled_at + timedelta(
            minutes=1
        )

        publication = service.mark_published(
            publication_id,
            published_at,
        )

        self.assertEqual(
            publication.status,
            PublicationStatus.PUBLISHED,
        )

        self.assertEqual(
            publication.published_at,
            published_at,
        )

        events = (
            self.event_repository.list_for_publication(
                publication_id
            )
        )

        self.assertGreaterEqual(
            len(events),
            5,
        )

    def test_complete_youtube_api_lifecycle(self):
        service = PublicationService(
            repository=self.repository,
            event_repository=self.event_repository,
            youtube_publisher=FakeYouTubePublisher(),
        )

        publication = service.create_publication(
            production_id="prod-001",
            package=self.package,
            mode=PublicationMode.YOUTUBE_API,
        )

        publication_id = publication.publication_id

        service.prepare_package(
            publication_id
        )

        service.request_approval(
            publication_id
        )

        service.approve(
            publication_id,
            approved_by="boss",
        )

        publication = service.upload(
            publication_id
        )

        self.assertEqual(
            publication.status,
            PublicationStatus.UPLOADED,
        )

        self.assertEqual(
            publication.youtube_video_id,
            "youtube-test-001",
        )

        self.assertEqual(
            publication.youtube_url,
            "https://youtube.example/watch?v=youtube-test-001",
        )

        self.assertIsNotNone(
            publication.uploaded_at
        )

    def test_failed_youtube_upload_moves_to_failed(self):
        service = PublicationService(
            repository=self.repository,
            event_repository=self.event_repository,
            youtube_publisher=FailingYouTubePublisher(),
        )

        publication = service.create_publication(
            production_id="prod-001",
            package=self.package,
            mode=PublicationMode.YOUTUBE_API,
        )

        publication_id = publication.publication_id

        service.prepare_package(
            publication_id
        )

        service.request_approval(
            publication_id
        )

        service.approve(
            publication_id,
            approved_by="boss",
        )

        with self.assertRaises(UploadError) as context:
            service.upload(
                publication_id
            )

        self.assertEqual(
            str(context.exception),
            "Simulated upload failure.",
        )

        publication = service.get(
            publication_id
        )

        self.assertEqual(
            publication.status,
            PublicationStatus.FAILED,
        )

        self.assertEqual(
            publication.error_message,
            "Simulated upload failure.",
        )

    def test_events_are_recorded_for_lifecycle(self):
        service = PublicationService(
            repository=self.repository,
            event_repository=self.event_repository,
        )

        publication = service.create_publication(
            production_id="prod-001",
            package=self.package,
            mode=PublicationMode.HUMAN,
        )

        publication_id = publication.publication_id

        service.prepare_package(
            publication_id
        )

        service.request_approval(
            publication_id
        )

        events = (
            self.event_repository.list_for_publication(
                publication_id
            )
        )

        self.assertGreaterEqual(
            len(events),
            3,
        )

        event_types = [
            event.event_type
            for event in events
        ]

        self.assertIn(
            "PUBLICATION_CREATED",
            event_types,
        )

        self.assertIn(
            "PACKAGE_READY",
            event_types,
        )

        self.assertIn(
            "APPROVAL_REQUESTED",
            event_types,
        )

    def test_unapproved_publication_cannot_upload(self):
        service = PublicationService(
            repository=self.repository,
            event_repository=self.event_repository,
            youtube_publisher=FakeYouTubePublisher(),
        )

        publication = service.create_publication(
            production_id="prod-001",
            package=self.package,
            mode=PublicationMode.YOUTUBE_API,
        )

        publication_id = publication.publication_id

        service.prepare_package(
            publication_id
        )

        service.request_approval(
            publication_id
        )

        with self.assertRaises(Exception):
            service.upload(
                publication_id
            )

    def test_publication_can_be_retrieved_after_creation(self):
        service = PublicationService(
            repository=self.repository,
            event_repository=self.event_repository,
        )

        publication = service.create_publication(
            production_id="prod-001",
            package=self.package,
            mode=PublicationMode.HUMAN,
        )

        publication_id = publication.publication_id

        stored = service.get(
            publication_id
        )

        self.assertEqual(
            stored.production_id,
            "prod-001",
        )

        self.assertEqual(
            stored.package.title,
            "Shadow Files — Test Episode",
        )


if __name__ == "__main__":
    unittest.main()
