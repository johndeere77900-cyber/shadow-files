"""
Tests for Shadow Files publication-package validation.
"""

import tempfile
import unittest
from pathlib import Path

from app.publishing.models import PublicationPackage
from app.publishing.package import (
    require_valid_publication_package,
    validate_publication_package,
)
from app.publishing.errors import PublicationValidationError


class TestPublicationPackageValidation(unittest.TestCase):
    def create_package(
        self,
        video_location: str,
        thumbnail_location: str,
    ) -> PublicationPackage:
        return PublicationPackage(
            production_id="prod-001",
            video_location=video_location,
            thumbnail_location=thumbnail_location,
            title="Shadow Files Episode",
            description="A completed episode.",
            tags=("true crime", "mystery"),
        )

    def test_valid_existing_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            video = Path(temp_dir) / "episode.mp4"
            thumbnail = Path(temp_dir) / "thumbnail.jpg"

            video.write_bytes(b"video")
            thumbnail.write_bytes(b"image")

            package = self.create_package(
                str(video),
                str(thumbnail),
            )

            result = validate_publication_package(
                package,
                check_files=True,
            )

            self.assertTrue(result.valid)
            self.assertEqual(result.errors, ())

    def test_missing_video_is_invalid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            thumbnail = Path(temp_dir) / "thumbnail.jpg"
            thumbnail.write_bytes(b"image")

            package = self.create_package(
                str(Path(temp_dir) / "missing.mp4"),
                str(thumbnail),
            )

            result = validate_publication_package(
                package,
                check_files=True,
            )

            self.assertFalse(result.valid)
            self.assertTrue(
                any("video file does not exist" in error
                    for error in result.errors)
            )

    def test_missing_thumbnail_is_invalid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            video = Path(temp_dir) / "episode.mp4"
            video.write_bytes(b"video")

            package = self.create_package(
                str(video),
                str(Path(temp_dir) / "missing.jpg"),
            )

            result = validate_publication_package(
                package,
                check_files=True,
            )

            self.assertFalse(result.valid)
            self.assertTrue(
                any("thumbnail file does not exist" in error
                    for error in result.errors)
            )

    def test_file_check_can_be_disabled(self):
        package = self.create_package(
            "/nonexistent/video.mp4",
            "/nonexistent/thumbnail.jpg",
        )

        result = validate_publication_package(
            package,
            check_files=False,
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.errors, ())

    def test_require_valid_raises_for_invalid_package(self):
        package = self.create_package(
            "/nonexistent/video.mp4",
            "/nonexistent/thumbnail.jpg",
        )

        with self.assertRaises(PublicationValidationError):
            require_valid_publication_package(
                package,
                check_files=True,
            )

    def test_require_valid_accepts_valid_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            video = Path(temp_dir) / "episode.mp4"
            thumbnail = Path(temp_dir) / "thumbnail.jpg"

            video.write_bytes(b"video")
            thumbnail.write_bytes(b"image")

            package = self.create_package(
                str(video),
                str(thumbnail),
            )

            require_valid_publication_package(
                package,
                check_files=True,
            )


if __name__ == "__main__":
    unittest.main()
