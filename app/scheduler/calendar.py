"""
Shadow Files calendar and recurring-schedule utilities.

The scheduler uses explicit calendar calculations rather than relying on
external calendar services. Timezone-aware datetimes are required.
"""

from datetime import datetime, timedelta
from typing import Optional

from app.scheduler.models import ScheduleSlot


def validate_schedule_window(
    scheduled_for: datetime,
    deadline: Optional[datetime] = None,
) -> None:
    """
    Validate a scheduled execution time and optional deadline.
    """

    if scheduled_for.tzinfo is None:
        raise ValueError(
            "Scheduled time must be timezone-aware."
        )

    if deadline is not None:
        if deadline.tzinfo is None:
            raise ValueError(
                "Deadline must be timezone-aware."
            )

        if deadline > scheduled_for:
            raise ValueError(
                "Deadline cannot be after scheduled time."
            )


def is_due(
    slot: ScheduleSlot,
    now: datetime,
) -> bool:
    """
    Return True when a planned or active slot has reached its
    scheduled execution time.
    """

    if now.tzinfo is None:
        raise ValueError(
            "Current time must be timezone-aware."
        )

    if slot.status.value not in {
        "PLANNED",
        "ACTIVE",
    }:
        return False

    return now >= slot.scheduled_for


def is_overdue(
    slot: ScheduleSlot,
    now: datetime,
) -> bool:
    """
    Return True when a slot has passed its scheduled time without
    reaching a completed state.
    """

    if now.tzinfo is None:
        raise ValueError(
            "Current time must be timezone-aware."
        )

    if slot.status.value == "COMPLETED":
        return False

    return now > slot.scheduled_for


def calculate_deadline(
    scheduled_for: datetime,
    preparation_minutes: int,
) -> datetime:
    """
    Calculate a preparation deadline before a scheduled event.
    """

    if scheduled_for.tzinfo is None:
        raise ValueError(
            "Scheduled time must be timezone-aware."
        )

    if preparation_minutes < 0:
        raise ValueError(
            "Preparation minutes cannot be negative."
        )

    return scheduled_for - timedelta(
        minutes=preparation_minutes
    )


def next_weekly_occurrence(
    start: datetime,
    weekday: int,
    hour: int,
    minute: int = 0,
) -> datetime:
    """
    Return the next occurrence of a weekly schedule.

    weekday uses Python's convention:
    Monday = 0 ... Sunday = 6.
    """

    if start.tzinfo is None:
        raise ValueError(
            "Start time must be timezone-aware."
        )

    if weekday < 0 or weekday > 6:
        raise ValueError(
            "Weekday must be between 0 and 6."
        )

    if hour < 0 or hour > 23:
        raise ValueError(
            "Hour must be between 0 and 23."
        )

    if minute < 0 or minute > 59:
        raise ValueError(
            "Minute must be between 0 and 59."
        )

    candidate = start.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0,
    )

    days_ahead = (
        weekday - candidate.weekday()
    ) % 7

    candidate += timedelta(
        days=days_ahead
    )

    if candidate < start:
        candidate += timedelta(
            days=7
        )

    return candidate 
