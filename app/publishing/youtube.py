"""
YouTube publishing provider abstractions for Shadow Files.

The interface deliberately separates the publishing engine from the
actual YouTube implementation. This allows human/manual publication
to remain available while automated YouTube API publication can be
qualified independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol

from .errors import PublisherUnavailableError


@dataclass(frozen=True)
class YouTubeUploadRequest:
    """Information required to upload a completed Shadow Files video."""

    video_location: str
    title: str
    description: str
    tags: tuple[str, ...] = ()
    category_id: Optional[str] = None
    thumbnail_location: Optional[str] = None
    privacy_status: str = "private"
    scheduled_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.video_location.strip():
            raise ValueError("video_location is required")

        if not self.title.strip():
            raise ValueError("title is required")

        if not self.description.strip():
            raise ValueError("description is required")

        if self.privacy_status not in {
            "private",
            "unlisted",
            "public",
        }:
            raise ValueError(
                "privacy_status must be private, unlisted, or public"
            )

        if self.scheduled_at is not None and self.scheduled_at.tzinfo is None:
            raise ValueError("scheduled_at must be timezone-aware")


@dataclass(frozen=True)
class YouTubeUploadResult:
    """Result returned by a YouTube publisher."""

    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    error_message: Optional[str] = None


class YouTubePublisher(Protocol):
    """
    Provider contract for automated YouTube publication.

    Implementations must not publish content unless the publishing
    service has already established the required approval state.
    """

    def upload(
        self,
        request: YouTubeUploadRequest,
    ) -> YouTubeUploadResult:
        ...


class NullYouTubePublisher:
    """
    Safe default publisher.

    It intentionally performs no external upload. This keeps the
    application runnable before YouTube API credentials and provider
    qualification are available.
    """

    def upload(
        self,
        request: YouTubeUploadRequest,
    ) -> YouTubeUploadResult:
        raise PublisherUnavailableError(
            "Automated YouTube publishing is not configured."
      )
