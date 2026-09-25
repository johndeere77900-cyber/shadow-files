"""
Publication event persistence for Shadow Files.

Publication events provide an append-only audit trail for important
publication lifecycle actions.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass(frozen=True)
class PublicationEvent:
    """Immutable publication lifecycle event."""

    event_id: str
    publication_id: str
    event_type: str
    created_at: datetime
    status: Optional[str] = None
    actor: Optional[str] = None
    details: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id is required")

        if not self.publication_id.strip():
            raise ValueError("publication_id is required")

        if not self.event_type.strip():
            raise ValueError("event_type is required")

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")


class PublicationEventRepository:
    """Append-only repository for publication events."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def record(
        self,
        publication_id: str,
        event_type: str,
        *,
        status: Optional[str] = None,
        actor: Optional[str] = None,
        details: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> PublicationEvent:
        """Record a new publication event."""

        event = PublicationEvent(
            event_id=str(uuid4()),
            publication_id=publication_id,
            event_type=event_type,
            status=status,
            actor=actor,
            details=details,
            created_at=created_at or datetime.now(timezone.utc),
        )

        self.connection.execute(
            """
            INSERT INTO publication_events (
                event_id,
                publication_id,
                event_type,
                status,
                actor,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.publication_id,
                event.event_type,
                event.status,
                event.actor,
                event.details,
                event.created_at.isoformat(),
            ),
        )

        self.connection.commit()
        return event

    def list_for_publication(
        self,
        publication_id: str,
    ) -> list[PublicationEvent]:
        """Return events for a publication in chronological order."""

        rows = self.connection.execute(
            """
            SELECT
                event_id,
                publication_id,
                event_type,
                status,
                actor,
                details,
                created_at
            FROM publication_events
            WHERE publication_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (publication_id,),
        ).fetchall()

        return [
            PublicationEvent(
                event_id=row["event_id"],
                publication_id=row["publication_id"],
                event_type=row["event_type"],
                status=row["status"],
                actor=row["actor"],
                details=row["details"],
                created_at=datetime.fromisoformat(
                    row["created_at"]
                ),
            )
            for row in rows
  ]
