"""
Tests for Shadow Files YouTube publishing abstractions.
"""

import unittest
from datetime import datetime, timezone

from app.publishing.errors import PublisherUnavailableError
from app.publishing.youtube import (
    NullYouTubePublisher,
    YouTubeUploadRequest,
    YouTubeUploadResult,
)


class TestYouTubeUploadRequest(unittest.TestCase):
    def test_valid_request(self):
        request = YouTubeUploadRequest(
            video_location="/videos/episode.mp4",
            title="Shadow Files Episode",
            description="Episode description.",
            tags=("true crime", "mystery"),
            category_id="24",
            thumbnail_location="/images/thumbnail.jpg",
        )

        self.assertEqual(
            request.video_location,
            "/videos/episode.mp4",
        )
        self.assertEqual(
            request.privacy_status,
            "private",
        )

    def test_empty_video_location_rejected(self):
        with self.assertRaises(ValueError):
            YouTubeUploadRequest(
                video_location="",
                title="Title",
                description="Description",
            )

    def test_empty_title_rejected(self):
        with self.assertRaises(ValueError):
            YouTubeUploadRequest(
                video_location="/video.mp4",
                title="",
                description="Description",
            )

    def test_empty_description_rejected(self):
        with self.assertRaises(ValueError):
            YouTubeUploadRequest(
                video_location="/video.mp4",
                title="Title",
                description="",
            )

    def test_invalid_privacy_status_rejected(self):
        with self.assertRaises(ValueError):
            YouTubeUploadRequest(
                video_location="/video.mp4",
                title="Title",
                description="Description",
                privacy_status="invalid",
            )

    def test_scheduled_at_must_be_timezone_aware(self):
        with self.assertRaises(ValueError):
            YouTubeUploadRequest(
                video_location="/video.mp4",
                title="Title",
                description="Description",
                scheduled_at=datetime.now(),
            )


class TestYouTubeUploadResult(unittest.TestCase):
    def test_successful_result(self):
        now = datetime.now(timezone.utc)

        result = YouTubeUploadResult(
            success=True,
            video_id="youtube-123",
            video_url="https://youtube.example/video",
            uploaded_at=now,
        )

        self.assertTrue(result.success)
        self.assertEqual(
            result.video_id,
            "youtube-123",
        )
        self.assertEqual(
            result.uploaded_at,
            now,
        )

    def test_failed_result(self):
        result = YouTubeUploadResult(
            success=False,
            error_message="Upload failed.",
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.video_id)
        self.assertEqual(
            result.error_message,
            "Upload failed.",
        )


class TestNullYouTubePublisher(unittest.TestCase):
    def test_upload_is_not_available(self):
        publisher = NullYouTubePublisher()

        request = YouTubeUploadRequest(
            video_location="/video.mp4",
            title="Title",
            description="Description",
        )

        with self.assertRaises(PublisherUnavailableError):
            publisher.upload(request)


if __name__ == "__main__":
    unittest.main()
