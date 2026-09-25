"""
Shadow Files production event tracking.

Every production status transition can be recorded as an explicit
event so lifecycle history remains auditable.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ProductionEvent:
    """Immutable record of a production lifecycle event."""

    event_id: str
    production_id: str
    from_status: Optional[str]
    to_status: str
    occurred_at: datetime
    reason: str

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("Event ID is required.")

        if not self.production_id.strip():
            raise ValueError(
                "Production ID is required."
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


class ProductionEventRepository:
    """Persistence operations for production lifecycle events."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def create(
        self,
        event: ProductionEvent,
    ) -> None:
        """Persist a production lifecycle event."""

        self._connection.execute(
            """
            INSERT INTO production_events (
                event_id,
                production_id,
                from_status,
                to_status,
                occurred_at,
                reason
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.production_id,
                event.from_status,
                event.to_status,
                event.occurred_at.isoformat(),
                event.reason,
            ),
        )
        self._connection.commit()

    def list_for_production(
        self,
        production_id: str,
    ) -> list[ProductionEvent]:
        """Return lifecycle events in chronological order."""

        rows = self._connection.execute(
            """
            SELECT
                event_id,
                production_id,
                from_status,
                to_status,
                occurred_at,
                reason
            FROM production_events
            WHERE production_id = ?
            ORDER BY occurred_at ASC, event_id ASC
            """,
            (production_id,),
        ).fetchall()

        return [
            ProductionEvent(
                event_id=row["event_id"],
                production_id=row["production_id"],
                from_status=row["from_status"],
                to_status=row["to_status"],
                occurred_at=datetime.fromisoformat(
                    row["occurred_at"]
                ),
                reason=row["reason"],
            )
            for row in rows
      ]
