"""
Shadow Files scheduler-status transition rules.

Schedule state changes are explicit so a scheduled production or
publication cannot silently move between lifecycle states.
"""

from app.scheduler.models import ScheduleStatus


class InvalidScheduleTransition(ValueError):
    """Raised when an invalid schedule transition is requested."""


_ALLOWED_TRANSITIONS = {
    ScheduleStatus.PLANNED: {
        ScheduleStatus.ACTIVE,
        ScheduleStatus.BLOCKED,
        ScheduleStatus.PAUSED,
        ScheduleStatus.CANCELLED,
        ScheduleStatus.MISSED,
    },
    ScheduleStatus.ACTIVE: {
        ScheduleStatus.COMPLETED,
        ScheduleStatus.MISSED,
        ScheduleStatus.BLOCKED,
        ScheduleStatus.PAUSED,
        ScheduleStatus.CANCELLED,
    },
    ScheduleStatus.COMPLETED: set(),
    ScheduleStatus.MISSED: {
        ScheduleStatus.PLANNED,
        ScheduleStatus.CANCELLED,
    },
    ScheduleStatus.BLOCKED: {
        ScheduleStatus.PLANNED,
        ScheduleStatus.ACTIVE,
        ScheduleStatus.PAUSED,
        ScheduleStatus.CANCELLED,
    },
    ScheduleStatus.PAUSED: {
        ScheduleStatus.PLANNED,
        ScheduleStatus.ACTIVE,
        ScheduleStatus.BLOCKED,
        ScheduleStatus.CANCELLED,
    },
    ScheduleStatus.CANCELLED: set(),
}


def validate_transition(
    current: ScheduleStatus,
    target: ScheduleStatus,
) -> None:
    """
    Validate a requested schedule-state transition.

    Raises:
        InvalidScheduleTransition:
            If the requested transition is not explicitly permitted.
    """

    if not isinstance(current, ScheduleStatus):
        raise TypeError(
            "Current status must be a ScheduleStatus."
        )

    if not isinstance(target, ScheduleStatus):
        raise TypeError(
            "Target status must be a ScheduleStatus."
        )

    if target not in _ALLOWED_TRANSITIONS[current]:
        raise InvalidScheduleTransition(
            f"Invalid schedule transition: "
            f"{current.value} -> {target.value}"
        )


def allowed_transitions(
    current: ScheduleStatus,
) -> frozenset[ScheduleStatus]:
    """Return the explicitly permitted next states."""

    if not isinstance(current, ScheduleStatus):
        raise TypeError(
            "Current status must be a ScheduleStatus."
        )

    return frozenset(
        _ALLOWED_TRANSITIONS[current]
)
