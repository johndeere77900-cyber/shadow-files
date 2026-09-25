"""
Shadow Files recurrence rules.

Provides controlled recurring publication-slot generation without
performing any external scheduling or publishing operations.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List


@dataclass(frozen=True)
class WeeklyScheduleRule:
    """Configuration for a weekly recurring schedule."""

    weekday: int
    hour: int
    minute: int = 0
    occurrences: int = 1

    def __post_init__(self) -> None:
        if not 0 <= self.weekday <= 6:
            raise ValueError(
                "Weekday must be between 0 and 6."
            )

        if not 0 <= self.hour <= 23:
            raise ValueError(
                "Hour must be between 0 and 23."
            )

        if not 0 <= self.minute <= 59:
            raise ValueError(
                "Minute must be between 0 and 59."
            )

        if self.occurrences < 1:
            raise ValueError(
                "Occurrences must be at least 1."
            )


def generate_weekly_occurrences(
    start: datetime,
    rule: WeeklyScheduleRule,
) -> List[datetime]:
    """
    Generate timezone-aware weekly schedule occurrences.

    The first returned occurrence is the first matching date/time that
    is not earlier than the supplied start time.
    """

    if start.tzinfo is None:
        raise ValueError(
            "Start time must be timezone-aware."
        )

    candidate = start.replace(
        hour=rule.hour,
        minute=rule.minute,
        second=0,
        microsecond=0,
    )

    days_ahead = (
        rule.weekday - candidate.weekday()
    ) % 7

    candidate += timedelta(
        days=days_ahead
    )

    if candidate < start:
        candidate += timedelta(
            days=7
        )

    return [
        candidate + timedelta(
            days=7 * index
        )
        for index in range(rule.occurrences)
]
