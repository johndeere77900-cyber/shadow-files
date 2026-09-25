"""
Shadow Files schedule planner.

Builds controlled production and publication schedule slots from
explicit planning inputs. It does not execute or publish anything.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from app.scheduler.models import (
    ScheduleSlot,
    ScheduleStatus,
    ScheduleType,
)


@dataclass(frozen=True)
class ProductionSchedulePlan:
    """Planning configuration for a production schedule."""

    production_id: str
    production_time: datetime
    preparation_hours: int = 24
    timezone_name: str = "UTC"
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.production_id.strip():
            raise ValueError(
                "Production ID is required."
            )

        if self.production_time.tzinfo is None:
            raise ValueError(
                "Production time must be timezone-aware."
            )

        if self.preparation_hours < 0:
            raise ValueError(
                "Preparation hours cannot be negative."
            )

        if not self.timezone_name.strip():
            raise ValueError(
                "Timezone name is required."
            )


def build_production_schedule(
    plan: ProductionSchedulePlan,
    schedule_id: str,
) -> ScheduleSlot:
    """
    Build a production schedule with a preparation deadline.
    """

    deadline = (
        plan.production_time
        - timedelta(
            hours=plan.preparation_hours
        )
    )

    return ScheduleSlot(
        schedule_id=schedule_id,
        production_id=plan.production_id,
        schedule_type=ScheduleType.PRODUCTION,
        scheduled_for=plan.production_time,
        status=ScheduleStatus.PLANNED,
        deadline=deadline,
        timezone_name=plan.timezone_name,
        notes=plan.notes,
    )


@dataclass(frozen=True)
class PublicationSchedulePlan:
    """Planning configuration for a publication slot."""

    production_id: str
    publication_time: datetime
    preparation_hours: int = 24
    timezone_name: str = "UTC"
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.production_id.strip():
            raise ValueError(
                "Production ID is required."
            )

        if self.publication_time.tzinfo is None:
            raise ValueError(
                "Publication time must be timezone-aware."
            )

        if self.preparation_hours < 0:
            raise ValueError(
                "Preparation hours cannot be negative."
            )

        if not self.timezone_name.strip():
            raise ValueError(
                "Timezone name is required."
            )


def build_publication_schedule(
    plan: PublicationSchedulePlan,
    schedule_id: str,
) -> ScheduleSlot:
    """
    Build a publication schedule with a preparation deadline.

    Publication remains a separate lifecycle from production. The
    scheduler does not perform the upload or publishing action.
    """

    deadline = (
        plan.publication_time
        - timedelta(
            hours=plan.preparation_hours
        )
    )

    return ScheduleSlot(
        schedule_id=schedule_id,
        production_id=plan.production_id,
        schedule_type=ScheduleType.PUBLICATION,
        scheduled_for=plan.publication_time,
        status=ScheduleStatus.PLANNED,
        deadline=deadline,
        timezone_name=plan.timezone_name,
        notes=plan.notes,
    )


def build_schedule_pair(
    production_id: str,
    production_time: datetime,
    publication_time: datetime,
    timezone_name: str = "UTC",
    preparation_hours: int = 24,
) -> List[ScheduleSlot]:
    """
    Build the production and publication slots for one episode.
    """

    if production_time.tzinfo is None:
        raise ValueError(
            "Production time must be timezone-aware."
        )

    if publication_time.tzinfo is None:
        raise ValueError(
            "Publication time must be timezone-aware."
        )

    if publication_time < production_time:
        raise ValueError(
            "Publication time cannot precede production time."
        )

    production_plan = ProductionSchedulePlan(
        production_id=production_id,
        production_time=production_time,
        preparation_hours=preparation_hours,
        timezone_name=timezone_name,
    )

    publication_plan = PublicationSchedulePlan(
        production_id=production_id,
        publication_time=publication_time,
        preparation_hours=preparation_hours,
        timezone_name=timezone_name,
    )

    return [
        build_production_schedule(
            production_plan,
            f"{production_id}-production",
        ),
        build_publication_schedule(
            publication_plan,
            f"{production_id}-publication",
        ),
    ]
