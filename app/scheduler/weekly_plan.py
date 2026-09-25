"""
Shadow Files weekly publication planning.

Provides the default recurring publication cadence for the channel:
four videos per month, with Tuesday as the default publication day.

Exact publication time and timezone remain configurable.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List


@dataclass(frozen=True)
class WeeklyPublicationRule:
    """Configurable recurring publication rule."""

    weekday: int = 1
    hour: int = 20
    minute: int = 0
    timezone_name: str = "UTC"
    occurrences: int = 4

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

        if not self.timezone_name.strip():
            raise ValueError(
                "Timezone name is required."
            )

        if self.occurrences < 1:
            raise ValueError(
                "Occurrences must be at least 1."
            )


def next_publication_time(
    start: datetime,
    rule: WeeklyPublicationRule,
) -> datetime:
    """
    Return the next publication time matching the configured weekday
    and clock time.
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

    return candidate


def build_monthly_publication_plan(
    start: datetime,
    rule: WeeklyPublicationRule,
) -> List[datetime]:
    """
    Build the configured number of recurring weekly publication slots.

    The function does not publish anything and does not reserve a
    platform slot. It only calculates planned timestamps.
    """

    first = next_publication_time(
        start,
        rule,
    )

    return [
        first + timedelta(
            weeks=index
        )
        for index in range(rule.occurrences)
      ]
