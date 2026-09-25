"""
Tests for Shadow Files publishing models.
"""

import unittest
from datetime import datetime, timezone

from app.publishing.models import (
    Publication,
    PublicationMode,
    PublicationPackage,
)
from app.publishing.status import PublicationStatus


class TestPublicationPackage(unittest.TestCase):
    def setUp(self):
        self.package = PublicationPackage(
            production_id="prod-001",
            video_location="/videos/episode.mp4",
            thumbnail_location="/images/thumbnail.jpg",
            title="Shadow Files Episode",
            description="A completed Shadow Files episode.",
            tags=("true crime", "mystery"),
            category_id="24",
            playlist_id="playlist-001",
            disclosure="Dramatized reconstruction used where applicable.",
        )

    def test_valid_package(self):
        self.assertEqual(
            self.package.production_id,
            "prod-001",
        )
        self.assertEqual(
            self.package.tags,
            ("true crime", "mystery"),
        )

    def test_empty_production_id_rejected(self):
        with self.assertRaises(ValueError):
            PublicationPackage(
                production_id="",
                video_location="/videos/episode.mp4",
                thumbnail_location="/images/thumbnail.jpg",
                title="Title",
                description="Description",
            )

    def test_empty_video_location_rejected(self):
        with self.assertRaises(ValueError):
            PublicationPackage(
                production_id="prod-001",
                video_location="",
                thumbnail_location="/images/thumbnail.jpg",
                title="Title",
                description="Description",
            )

    def test_empty_thumbnail_location_rejected(self):
        with self.assertRaises(ValueError):
            PublicationPackage(
                production_id="prod-001",
                video_location="/videos/episode.mp4",
                thumbnail_location="",
                title="Title",
                description="Description",
            )

    def test_empty_title_rejected(self):
        with self.assertRaises(ValueError):
            PublicationPackage(
                production_id="prod-001",
                video_location="/videos/episode.mp4",
                thumbnail_location="/images/thumbnail.jpg",
                title="",
                description="Description",
            )

    def test_empty_description_rejected(self):
        with self.assertRaises(ValueError):
            PublicationPackage(
                production_id="prod-001",
                video_location="/videos/episode.mp4",
                thumbnail_location="/images/thumbnail.jpg",
                title="Title",
                description="",
            )

    def test_empty_tag_rejected(self):
        with self.assertRaises(ValueError):
            PublicationPackage(
                production_id="prod-001",
                video_location="/videos/episode.mp4",
                thumbnail_location="/images/thumbnail.jpg",
                title="Title",
                description="Description",
                tags=("true crime", ""),
            )


class TestPublication(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)

        self.package = PublicationPackage(
            production_id="prod-001",
            video_location="/videos/episode.mp4",
            thumbnail_location="/images/thumbnail.jpg",
            title="Shadow Files Episode",
            description="A completed Shadow Files episode.",
        )

    def test_valid_publication(self):
        publication = Publication(
            publication_id="pub-001",
            production_id="prod-001",
            mode=PublicationMode.HUMAN,
            status=PublicationStatus.NOT_STARTED,
            package=self.package,
            created_at=self.now,
            updated_at=self.now,
        )

        self.assertEqual(
            publication.publication_id,
            "pub-001",
        )
        self.assertEqual(
            publication.mode,
            PublicationMode.HUMAN,
        )
        self.assertEqual(
            publication.status,
            PublicationStatus.NOT_STARTED,
        )

    def test_package_production_must_match(self):
        package = PublicationPackage(
            production_id="different-production",
            video_location="/videos/episode.mp4",
            thumbnail_location="/images/thumbnail.jpg",
            title="Title",
            description="Description",
        )

        with self.assertRaises(ValueError):
            Publication(
                publication_id="pub-001",
                production_id="prod-001",
                mode=PublicationMode.HUMAN,
                status=PublicationStatus.NOT_STARTED,
                package=package,
                created_at=self.now,
                updated_at=self.now,
            )

    def test_naive_created_at_rejected(self):
        naive = datetime.now()

        with self.assertRaises(ValueError):
            Publication(
                publication_id="pub-001",
                production_id="prod-001",
                mode=PublicationMode.HUMAN,
                status=PublicationStatus.NOT_STARTED,
                package=self.package,
                created_at=naive,
                updated_at=self.now,
            )

    def test_naive_updated_at_rejected(self):
        naive = datetime.now()

        with self.assertRaises(ValueError):
            Publication(
                publication_id="pub-001",
                production_id="prod-001",
                mode=PublicationMode.HUMAN,
                status=PublicationStatus.NOT_STARTED,
                package=self.package,
                created_at=self.now,
                updated_at=naive,
            )

    def test_updated_at_before_created_at_rejected(self):
        later = self.now.replace(
            microsecond=self.now.microsecond + 1
        )

        with self.assertRaises(ValueError):
            Publication(
                publication_id="pub-001",
                production_id="prod-001",
                mode=PublicationMode.HUMAN,
                status=PublicationStatus.NOT_STARTED,
                package=self.package,
                created_at=later,
                updated_at=self.now,
            )

    def test_optional_timestamps_must_be_timezone_aware(self):
        with self.assertRaises(ValueError):
            Publication(
                publication_id="pub-001",
                production_id="prod-001",
                mode=PublicationMode.HUMAN,
                status=PublicationStatus.NOT_STARTED,
                package=self.package,
                created_at=self.now,
                updated_at=self.now,
                approved_at=datetime.now(),
            )


if __name__ == "__main__":
    unittest.main()
