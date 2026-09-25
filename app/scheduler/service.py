"""
Shadow Files scheduler service.

Coordinates schedule creation and lifecycle transitions while enforcing
explicit scheduler state rules.
"""

from datetime import datetime
from typing import Optional

from app.scheduler.models import (
    ScheduleSlot,
    ScheduleStatus,
    ScheduleType,
)
from app.scheduler.repository import ScheduleRepository
from app.scheduler.status import validate_transition


class SchedulerService:
    """Application service for controlled scheduling workflows."""

    def __init__(
        self,
        repository: ScheduleRepository,
    ) -> None:
        self.repository = repository

    def create_schedule(
        self,
        schedule_id: str,
        production_id: str,
        schedule_type: ScheduleType,
        scheduled_for: datetime,
        deadline: Optional[datetime] = None,
        timezone_name: str = "UTC",
        notes: str = "",
    ) -> ScheduleSlot:
        """Create a planned schedule slot."""

        slot = ScheduleSlot(
            schedule_id=schedule_id,
            production_id=production_id,
            schedule_type=schedule_type,
            scheduled_for=scheduled_for,
            status=ScheduleStatus.PLANNED,
            deadline=deadline,
            timezone_name=timezone_name,
            notes=notes,
        )

        self.repository.create(slot)

        return slot

    def get_schedule(
        self,
        schedule_id: str,
    ) -> Optional[ScheduleSlot]:
        """Retrieve a schedule by ID."""

        return self.repository.get(
            schedule_id
        )

    def transition(
        self,
        schedule_id: str,
        target_status: ScheduleStatus,
    ) -> ScheduleSlot:
        """Move a schedule to an explicitly permitted state."""

        slot = self.repository.get(
            schedule_id
        )

        if slot is None:
            raise KeyError(
                f"Schedule not found: {schedule_id}"
            )

        validate_transition(
            slot.status,
            target_status,
        )

        return self.repository.update_status(
            schedule_id,
            target_status,
        )

    def activate(
        self,
        schedule_id: str,
    ) -> ScheduleSlot:
        """Activate a planned schedule."""

        return self.transition(
            schedule_id,
            ScheduleStatus.ACTIVE,
        )

    def complete(
        self,
        schedule_id: str,
    ) -> ScheduleSlot:
        """Mark an active schedule as completed."""

        return self.transition(
            schedule_id,
            ScheduleStatus.COMPLETED,
        )

    def mark_missed(
        self,
        schedule_id: str,
    ) -> ScheduleSlot:
        """Mark a schedule as missed."""

        return self.transition(
            schedule_id,
            ScheduleStatus.MISSED,
        )

    def block(
        self,
        schedule_id: str,
    ) -> ScheduleSlot:
        """Block a schedule requiring intervention."""

        return self.transition(
            schedule_id,
            ScheduleStatus.BLOCKED,
        )

    def pause(
        self,
        schedule_id: str,
    ) -> ScheduleSlot:
        """Pause a schedule."""

        return self.transition(
            schedule_id,
            ScheduleStatus.PAUSED,
        )

    def cancel(
        self,
        schedule_id: str,
    ) -> ScheduleSlot:
        """Cancel a schedule."""

        return self.transition(
            schedule_id,
            ScheduleStatus.CANCELLED,
        )

    def list_due(
        self,
        now: datetime,
    ) -> list[ScheduleSlot]:
        """Return schedules whose execution time has arrived."""

        return self.repository.list_due(
            now
    )
