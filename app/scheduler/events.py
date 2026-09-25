"""
Shadow Files scheduler event tracking.

Every schedule status transition can be recorded as an explicit,
append-only lifecycle event for auditability.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ScheduleEvent:
    """Immutable record of a schedule lifecycle event."""

    event_id: str
    schedule_id: str
    from_status: Optional[str]
    to_status: str
    occurred_at: datetime
    reason: str

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError(
                "Event ID is required."
            )

        if not self.schedule_id.strip():
            raise ValueError(
                "Schedule ID is required."
            )

        if not self.to_status.strip():
            raise ValueError(
                "Target status is required."
            )

        if self.occurred_at.tzinfo is None:
            raise ValueError(
                "Event timestamp must be timezone-aware."
            )

        if not self.reason.strip():
            raise ValueError(
                "Event reason is required."
            )


class ScheduleEventRepository:
    """Persistence operations for scheduler lifecycle events."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def create(
        self,
        event: ScheduleEvent,
    ) -> None:
        """Persist a scheduler lifecycle event."""

        self._connection.execute(
            """
            INSERT INTO schedule_events (
                event_id,
                schedule_id,
                from_status,
                to_status,
                occurred_at,
                reason
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.schedule_id,
                event.from_status,
                event.to_status,
                event.occurred_at.isoformat(),
                event.reason,
            ),
        )

        self._connection.commit()

    def list_for_schedule(
        self,
        schedule_id: str,
    ) -> list[ScheduleEvent]:
        """Return scheduler events chronologically."""

        rows = self._connection.execute(
            """
            SELECT
                event_id,
                schedule_id,
                from_status,
                to_status,
                occurred_at,
                reason
            FROM schedule_events
            WHERE schedule_id = ?
            ORDER BY occurred_at ASC, event_id ASC
            """,
            (schedule_id,),
        ).fetchall()

        return [
            ScheduleEvent(
                event_id=row["event_id"],
                schedule_id=row["schedule_id"],
                from_status=row["from_status"],
                to_status=row["to_status"],
                occurred_at=datetime.fromisoformat(
                    row["occurred_at"]
                ),
                reason=row["reason"],
            )
            for row in rows
  ]
