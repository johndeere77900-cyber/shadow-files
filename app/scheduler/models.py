"""
Shadow Files scheduler-domain models.

These models represent production and publication scheduling without
performing scheduling or publication themselves.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ScheduleStatus(str, Enum):
    """Lifecycle state of a scheduled item."""

    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
    BLOCKED = "BLOCKED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"


class ScheduleType(str, Enum):
    """Types of scheduling records."""

    PRODUCTION = "PRODUCTION"
    PUBLICATION = "PUBLICATION"


@dataclass(frozen=True)
class ScheduleSlot:
    """Immutable scheduled production or publication slot."""

    schedule_id: str
    production_id: str
    schedule_type: ScheduleType
    scheduled_for: datetime
    status: ScheduleStatus = ScheduleStatus.PLANNED
    deadline: Optional[datetime] = None
    timezone_name: str = "UTC"
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.schedule_id.strip():
            raise ValueError("Schedule ID is required.")

        if not self.production_id.strip():
            raise ValueError(
                "Production ID is required."
            )

        if not isinstance(
            self.schedule_type,
            ScheduleType,
        ):
            raise TypeError(
                "Schedule type must be a ScheduleType."
            )

        if not isinstance(
            self.status,
            ScheduleStatus,
        ):
            raise TypeError(
                "Schedule status must be a ScheduleStatus."
            )

        if self.scheduled_for.tzinfo is None:
            raise ValueError(
                "Scheduled time must be timezone-aware."
            )

        if self.deadline is not None:
            if self.deadline.tzinfo is None:
                raise ValueError(
                    "Schedule deadline must be timezone-aware."
                )

            if self.deadline > self.scheduled_for:
                raise ValueError(
                    "Schedule deadline cannot be after "
                    "the scheduled time."
                )

        if not self.timezone_name.strip():
            raise ValueError(
                "Timezone name is required."
            )
