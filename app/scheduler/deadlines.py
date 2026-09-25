"""
Shadow Files deadline management.

Provides deterministic deadline calculations for production and
publication workflows without executing scheduled actions.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class Deadline:
    """Immutable deadline record."""

    deadline_id: str
    production_id: str
    due_at: datetime
    label: str
    completed: bool = False

    def __post_init__(self) -> None:
        if not self.deadline_id.strip():
            raise ValueError(
                "Deadline ID is required."
            )

        if not self.production_id.strip():
            raise ValueError(
                "Production ID is required."
            )

        if self.due_at.tzinfo is None:
            raise ValueError(
                "Deadline time must be timezone-aware."
            )

        if not self.label.strip():
            raise ValueError(
                "Deadline label is required."
            )

        if not isinstance(self.completed, bool):
            raise TypeError(
                "Completed must be boolean."
            )


def calculate_deadline(
    target_time: datetime,
    hours_before: int,
) -> datetime:
    """
    Calculate a deadline before a target event.
    """

    if target_time.tzinfo is None:
        raise ValueError(
            "Target time must be timezone-aware."
        )

    if hours_before < 0:
        raise ValueError(
            "Hours before cannot be negative."
        )

    return target_time - timedelta(
        hours=hours_before
    )


def is_deadline_reached(
    deadline: Deadline,
    now: datetime,
) -> bool:
    """Return whether a deadline has been reached."""

    if now.tzinfo is None:
        raise ValueError(
            "Current time must be timezone-aware."
        )

    return now >= deadline.due_at


def is_deadline_overdue(
    deadline: Deadline,
    now: datetime,
) -> bool:
    """Return whether an incomplete deadline is overdue."""

    if now.tzinfo is None:
        raise ValueError(
            "Current time must be timezone-aware."
        )

    if deadline.completed:
        return False

    return now > deadline.due_at


def build_standard_deadlines(
    production_id: str,
    publication_time: datetime,
    research_hours: int = 168,
    script_hours: int = 72,
    production_hours: int = 24,
    qc_hours: int = 6,
) -> list[Deadline]:
    """
    Build standard backward-planned episode deadlines.

    The schedule is calculated backward from the intended publication
    time. All deadlines are explicit and independently auditable.
    """

    if publication_time.tzinfo is None:
        raise ValueError(
            "Publication time must be timezone-aware."
        )

    values = (
        ("research", research_hours),
        ("script", script_hours),
        ("production", production_hours),
        ("qc", qc_hours),
    )

    for label, hours in values:
        if hours < 0:
            raise ValueError(
                f"{label} hours cannot be negative."
            )

    qc_deadline = publication_time - timedelta(
        hours=qc_hours
    )

    production_deadline = qc_deadline - timedelta(
        hours=production_hours
    )

    script_deadline = production_deadline - timedelta(
        hours=script_hours
    )

    research_deadline = script_deadline - timedelta(
        hours=research_hours
    )

    return [
        Deadline(
            deadline_id=f"{production_id}-research",
            production_id=production_id,
            due_at=research_deadline,
            label="Research complete",
        ),
        Deadline(
            deadline_id=f"{production_id}-script",
            production_id=production_id,
            due_at=script_deadline,
            label="Script approved",
        ),
        Deadline(
            deadline_id=f"{production_id}-production",
            production_id=production_id,
            due_at=production_deadline,
            label="Production complete",
        ),
        Deadline(
            deadline_id=f"{production_id}-qc",
            production_id=production_id,
            due_at=qc_deadline,
            label="Quality control complete",
        ),
      ]
