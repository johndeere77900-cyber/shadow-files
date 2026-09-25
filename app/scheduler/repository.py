"""
Shadow Files scheduler repository.

Provides persistence operations for schedule slots while keeping
database access outside scheduler-domain models.
"""

import sqlite3
from datetime import datetime
from typing import Optional

from app.scheduler.models import (
    ScheduleSlot,
    ScheduleStatus,
    ScheduleType,
)


class ScheduleRepository:
    """Persistence operations for scheduler records."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def create(
        self,
        slot: ScheduleSlot,
    ) -> None:
        """Create a schedule slot."""

        self._connection.execute(
            """
            INSERT INTO schedule_slots (
                schedule_id,
                production_id,
                schedule_type,
                scheduled_for,
                status,
                deadline,
                timezone_name,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                slot.schedule_id,
                slot.production_id,
                slot.schedule_type.value,
                slot.scheduled_for.isoformat(),
                slot.status.value,
                (
                    slot.deadline.isoformat()
                    if slot.deadline is not None
                    else None
                ),
                slot.timezone_name,
                slot.notes,
            ),
        )

        self._connection.commit()

    def get(
        self,
        schedule_id: str,
    ) -> Optional[ScheduleSlot]:
        """Return a schedule slot by ID."""

        row = self._connection.execute(
            """
            SELECT
                schedule_id,
                production_id,
                schedule_type,
                scheduled_for,
                status,
                deadline,
                timezone_name,
                notes
            FROM schedule_slots
            WHERE schedule_id = ?
            """,
            (schedule_id,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def update_status(
        self,
        schedule_id: str,
        status: ScheduleStatus,
    ) -> ScheduleSlot:
        """Update a schedule status and return the updated slot."""

        existing = self.get(schedule_id)

        if existing is None:
            raise KeyError(
                f"Schedule not found: {schedule_id}"
            )

        updated = ScheduleSlot(
            schedule_id=existing.schedule_id,
            production_id=existing.production_id,
            schedule_type=existing.schedule_type,
            scheduled_for=existing.scheduled_for,
            status=status,
            deadline=existing.deadline,
            timezone_name=existing.timezone_name,
            notes=existing.notes,
        )

        self._connection.execute(
            """
            UPDATE schedule_slots
            SET status = ?
            WHERE schedule_id = ?
            """,
            (
                status.value,
                schedule_id,
            ),
        )

        self._connection.commit()

        return updated

    def list_for_production(
        self,
        production_id: str,
    ) -> list[ScheduleSlot]:
        """Return all schedules belonging to a production."""

        rows = self._connection.execute(
            """
            SELECT
                schedule_id,
                production_id,
                schedule_type,
                scheduled_for,
                status,
                deadline,
                timezone_name,
                notes
            FROM schedule_slots
            WHERE production_id = ?
            ORDER BY scheduled_for ASC, schedule_id ASC
            """,
            (production_id,),
        ).fetchall()

        return [
            self._from_row(row)
            for row in rows
        ]

    def list_due(
        self,
        now: datetime,
    ) -> list[ScheduleSlot]:
        """
        Return planned or active schedules whose scheduled time has
        arrived.
        """

        if now.tzinfo is None:
            raise ValueError(
                "Current time must be timezone-aware."
            )

        rows = self._connection.execute(
            """
            SELECT
                schedule_id,
                production_id,
                schedule_type,
                scheduled_for,
                status,
                deadline,
                timezone_name,
                notes
            FROM schedule_slots
            WHERE status IN (?, ?)
            ORDER BY scheduled_for ASC, schedule_id ASC
            """,
            (
                ScheduleStatus.PLANNED.value,
                ScheduleStatus.ACTIVE.value,
            ),
        ).fetchall()

        slots = [
            self._from_row(row)
            for row in rows
        ]

        return [
            slot
            for slot in slots
            if slot.scheduled_for <= now
        ]

    @staticmethod
    def _from_row(
        row: sqlite3.Row,
    ) -> ScheduleSlot:
        """Convert a database row into a scheduler model."""

        deadline = row["deadline"]

        return ScheduleSlot(
            schedule_id=row["schedule_id"],
            production_id=row["production_id"],
            schedule_type=ScheduleType(
                row["schedule_type"]
            ),
            scheduled_for=datetime.fromisoformat(
                row["scheduled_for"]
            ),
            status=ScheduleStatus(
                row["status"]
            ),
            deadline=(
                datetime.fromisoformat(deadline)
                if deadline is not None
                else None
            ),
            timezone_name=row["timezone_name"],
            notes=row["notes"],
      )
