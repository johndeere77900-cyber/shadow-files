"""
Repository layer for Shadow Files publications.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from datetime import datetime
from typing import Optional

from .models import Publication, PublicationMode, PublicationPackage
from .status import PublicationStatus, validate_transition


class PublicationRepository:
    """Persistence operations for publication records."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def create(self, publication: Publication) -> Publication:
        """Create a new publication record."""

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
                category_id,
                playlist_id,
                disclosure,
                approved_at,
                uploaded_at,
                scheduled_at,
                published_at,
                youtube_video_id,
                youtube_url,
                error_message,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                publication.publication_id,
                publication.production_id,
                publication.mode.value,
                publication.status.value,
                publication.package.video_location,
                publication.package.thumbnail_location,
                publication.package.title,
                publication.package.description,
                json.dumps(publication.package.tags),
                publication.package.category_id,
                publication.package.playlist_id,
                publication.package.disclosure,
                self._serialize_datetime(publication.approved_at),
                self._serialize_datetime(publication.uploaded_at),
                self._serialize_datetime(publication.scheduled_at),
                self._serialize_datetime(publication.published_at),
                publication.youtube_video_id,
                publication.youtube_url,
                publication.error_message,
                self._serialize_datetime(publication.created_at),
                self._serialize_datetime(publication.updated_at),
            ),
        )

        self.connection.commit()
        return publication

    def get(
        self,
        publication_id: str,
    ) -> Optional[Publication]:
        """Retrieve a publication by ID."""

        row = self.connection.execute(
            """
            SELECT *
            FROM publications
            WHERE publication_id = ?
            """,
            (publication_id,),
        ).fetchone()

        if row is None:
            return None

        return self._row_to_publication(row)

    def list_for_production(
        self,
        production_id: str,
    ) -> list[Publication]:
        """Return publications belonging to a production."""

        rows = self.connection.execute(
            """
            SELECT *
            FROM publications
            WHERE production_id = ?
            ORDER BY created_at ASC
            """,
            (production_id,),
        ).fetchall()

        return [self._row_to_publication(row) for row in rows]

    def update_status(
        self,
        publication_id: str,
        target_status: PublicationStatus,
        updated_at: datetime,
    ) -> Publication:
        """
        Transition a publication to a new status.

        Transition validation is enforced here so direct repository
        usage cannot silently bypass the publication lifecycle.
        """

        publication = self.get(publication_id)

        if publication is None:
            raise ValueError(
                f"Publication not found: {publication_id}"
            )

        validate_transition(
            publication.status,
            target_status,
        )

        if updated_at.tzinfo is None:
            raise ValueError("updated_at must be timezone-aware")

        if updated_at < publication.created_at:
            raise ValueError(
                "updated_at cannot be earlier than created_at"
            )

        updated_publication = replace(
            publication,
            status=target_status,
            updated_at=updated_at,
        )

        self.connection.execute(
            """
            UPDATE publications
            SET status = ?,
                updated_at = ?
            WHERE publication_id = ?
            """,
            (
                target_status.value,
                self._serialize_datetime(updated_at),
                publication_id,
            ),
        )

        self.connection.commit()
        return updated_publication

    def update_metadata(
        self,
        publication_id: str,
        *,
        approved_at: Optional[datetime] = None,
        uploaded_at: Optional[datetime] = None,
        scheduled_at: Optional[datetime] = None,
        published_at: Optional[datetime] = None,
        youtube_video_id: Optional[str] = None,
        youtube_url: Optional[str] = None,
        error_message: Optional[str] = None,
        updated_at: datetime,
    ) -> Publication:
        """Update publication lifecycle metadata."""

        publication = self.get(publication_id)

        if publication is None:
            raise ValueError(
                f"Publication not found: {publication_id}"
            )

        if updated_at.tzinfo is None:
            raise ValueError("updated_at must be timezone-aware")

        if updated_at < publication.created_at:
            raise ValueError(
                "updated_at cannot be earlier than created_at"
            )

        values = {
            "approved_at": approved_at,
            "uploaded_at": uploaded_at,
            "scheduled_at": scheduled_at,
            "published_at": published_at,
        }

        for name, value in values.items():
            if value is not None and value.tzinfo is None:
                raise ValueError(
                    f"{name} must be timezone-aware"
                )

        self.connection.execute(
            """
            UPDATE publications
            SET approved_at = ?,
                uploaded_at = ?,
                scheduled_at = ?,
                published_at = ?,
                youtube_video_id = ?,
                youtube_url = ?,
                error_message = ?,
                updated_at = ?
            WHERE publication_id = ?
            """,
            (
                self._serialize_datetime(approved_at),
                self._serialize_datetime(uploaded_at),
                self._serialize_datetime(scheduled_at),
                self._serialize_datetime(published_at),
                youtube_video_id,
                youtube_url,
                error_message,
                self._serialize_datetime(updated_at),
                publication_id,
            ),
        )

        self.connection.commit()

        result = self.get(publication_id)

        if result is None:
            raise RuntimeError(
                "Publication disappeared after metadata update"
            )

        return result

    @staticmethod
    def _serialize_datetime(
        value: Optional[datetime],
    ) -> Optional[str]:
        if value is None:
            return None

        return value.isoformat()

    @staticmethod
    def _deserialize_datetime(
        value: Optional[str],
    ) -> Optional[datetime]:
        if value is None:
            return None

        return datetime.fromisoformat(value)

    def _row_to_publication(
        self,
        row: sqlite3.Row,
    ) -> Publication:
        """Convert a database row into a Publication object."""

        package = PublicationPackage(
            production_id=row["production_id"],
            video_location=row["video_location"],
            thumbnail_location=row["thumbnail_location"],
            title=row["title"],
            description=row["description"],
            tags=tuple(json.loads(row["tags_json"])),
            category_id=row["category_id"],
            playlist_id=row["playlist_id"],
            disclosure=row["disclosure"],
        )

        created_at = self._deserialize_datetime(
            row["created_at"]
        )
        updated_at = self._deserialize_datetime(
            row["updated_at"]
        )

        if created_at is None or updated_at is None:
            raise ValueError(
                "Publication timestamps cannot be null"
            )

        return Publication(
            publication_id=row["publication_id"],
            production_id=row["production_id"],
            mode=PublicationMode(row["mode"]),
            status=PublicationStatus(row["status"]),
            package=package,
            created_at=created_at,
            updated_at=updated_at,
            approved_at=self._deserialize_datetime(
                row["approved_at"]
            ),
            uploaded_at=self._deserialize_datetime(
                row["uploaded_at"]
            ),
            scheduled_at=self._deserialize_datetime(
                row["scheduled_at"]
            ),
            published_at=self._deserialize_datetime(
                row["published_at"]
            ),
            youtube_video_id=row["youtube_video_id"],
            youtube_url=row["youtube_url"],
            error_message=row["error_message"],
      )
