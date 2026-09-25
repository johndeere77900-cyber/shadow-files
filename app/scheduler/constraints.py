"""
Shadow Files scheduler constraints.

These rules prevent the scheduler from creating impossible or unsafe
production timelines.
"""

from datetime import datetime
from typing import Iterable

from app.scheduler.models import ScheduleSlot


class ScheduleConstraintError(ValueError):
    """Raised when a schedule violates a scheduler constraint."""


def validate_slot_order(
    slots: Iterable[ScheduleSlot],
) -> None:
    """
    Validate that production occurs no later than publication.

    A schedule containing both production and publication slots for the
    same production must not place publication before production.
    """

    slot_list = list(slots)

    production_slots = {
        slot.production_id: slot
        for slot in slot_list
        if slot.schedule_type.value == "PRODUCTION"
    }

    publication_slots = {
        slot.production_id: slot
        for slot in slot_list
        if slot.schedule_type.value == "PUBLICATION"
    }

    for production_id, publication in publication_slots.items():
        production = production_slots.get(
            production_id
        )

        if production is None:
            continue

        if publication.scheduled_for < production.scheduled_for:
            raise ScheduleConstraintError(
                "Publication cannot be scheduled before production: "
                f"{production_id}"
            )


def validate_unique_schedule_ids(
    slots: Iterable[ScheduleSlot],
) -> None:
    """Reject duplicate schedule IDs."""

    seen: set[str] = set()

    for slot in slots:
        if slot.schedule_id in seen:
            raise ScheduleConstraintError(
                "Duplicate schedule ID: "
                f"{slot.schedule_id}"
            )

        seen.add(slot.schedule_id)


def validate_no_duplicate_type_for_production(
    slots: Iterable[ScheduleSlot],
) -> None:
    """
    Reject multiple slots of the same schedule type for one production.

    This prevents accidental duplicate publication or production slots
    from being silently treated as separate schedules.
    """

    seen: set[tuple[str, str]] = set()

    for slot in slots:
        key = (
            slot.production_id,
            slot.schedule_type.value,
        )

        if key in seen:
            raise ScheduleConstraintError(
                "Duplicate schedule type for production: "
                f"{slot.production_id} / "
                f"{slot.schedule_type.value}"
            )

        seen.add(key)


def validate_deadlines(
    slots: Iterable[ScheduleSlot],
) -> None:
    """
    Validate that every supplied deadline is earlier than or equal to
    its scheduled execution time.
    """

    for slot in slots:
        if slot.deadline is None:
            continue

        if slot.deadline > slot.scheduled_for:
            raise ScheduleConstraintError(
                "Schedule deadline occurs after scheduled time: "
                f"{slot.schedule_id}"
            )


def validate_schedule_set(
    slots: Iterable[ScheduleSlot],
) -> None:
    """
    Apply all scheduler-set integrity constraints.
    """

    slot_list = list(slots)

    validate_unique_schedule_ids(
        slot_list
    )

    validate_no_duplicate_type_for_production(
        slot_list
    )

    validate_deadlines(
        slot_list
    )

    validate_slot_order(
        slot_list
        )
