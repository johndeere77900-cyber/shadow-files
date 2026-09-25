"""
Publishing domain models for Shadow Files.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from .status import PublicationStatus


class PublicationMode(str, Enum):
    """
    Determines how a completed Shadow Files video is published.
    """

    HUMAN = "HUMAN"
    YOUTUBE_API = "YOUTUBE_API"


@dataclass(frozen=True)
class PublicationPackage:
    """
    Complete publication package for a Shadow Files episode.

    The package can be handed to a human for manual publication or
    supplied to an approved automated YouTube publisher.
    """

    production_id: str
    video_location: str
    thumbnail_location: str
    title: str
    description: str
    tags: tuple[str, ...] = ()
    category_id: Optional[str] = None
    playlist_id: Optional[str] = None
    disclosure: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.production_id.strip():
            raise ValueError("production_id is required")

        if not self.video_location.strip():
            raise ValueError("video_location is required")

        if not self.thumbnail_location.strip():
            raise ValueError("thumbnail_location is required")

        if not self.title.strip():
            raise ValueError("title is required")

        if not self.description.strip():
            raise ValueError("description is required")

        if any(not tag.strip() for tag in self.tags):
            raise ValueError("tags cannot contain empty values")


@dataclass(frozen=True)
class Publication:
    """
    Persistent publication record.

    Publication is deliberately separate from Production. A production
    may be complete without being approved or published.
    """

    publication_id: str
    production_id: str
    mode: PublicationMode
    status: PublicationStatus
    package: PublicationPackage
    created_at: datetime
    updated_at: datetime

    approved_at: Optional[datetime] = None
    uploaded_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    error_message: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.publication_id.strip():
            raise ValueError("publication_id is required")

        if not self.production_id.strip():
            raise ValueError("production_id is required")

        if self.package.production_id != self.production_id:
            raise ValueError(
                "package.production_id must match production_id"
            )

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

        if self.updated_at.tzinfo is None:
            raise ValueError("updated_at must be timezone-aware")

        if self.updated_at < self.created_at:
            raise ValueError(
                "updated_at cannot be earlier than created_at"
            )

        if self.approved_at is not None and self.approved_at.tzinfo is None:
            raise ValueError("approved_at must be timezone-aware")

        if self.uploaded_at is not None and self.uploaded_at.tzinfo is None:
            raise ValueError("uploaded_at must be timezone-aware")

        if self.scheduled_at is not None and self.scheduled_at.tzinfo is None:
            raise ValueError("scheduled_at must be timezone-aware")

        if self.published_at is not None and self.published_at.tzinfo is None:
            raise ValueError("published_at must be timezone-aware")
