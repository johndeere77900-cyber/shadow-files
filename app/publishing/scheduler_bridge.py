"""
Bridge between Shadow Files publication records and the scheduler.

The scheduler owns timing.
The publishing service owns publication state.

This module keeps those responsibilities separate while allowing a
publication to be connected to an existing schedule.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .errors import PublicationValidationError
from .models import Publication
from .status import PublicationStatus


def validate_publication_schedule(
    publication: Publication,
    *,
    scheduled_at: datetime,
) -> None:
    """
    Validate that a publication can receive a schedule.

    The publication must already have a successful upload recorded.
    """

    if scheduled_at.tzinfo is None:
        raise ValueError(
            "scheduled_at must be timezone-aware"
        )

    if publication.status != PublicationStatus.UPLOADED:
        raise PublicationValidationError(
            "Only an UPLOADED publication can receive a "
            "publication schedule."
        )


def build_publication_schedule_data(
    publication: Publication,
    *,
    scheduled_at: datetime,
) -> dict[str, Any]:
    """
    Build scheduler-compatible data without directly modifying
    scheduler records.
    """

    validate_publication_schedule(
        publication,
        scheduled_at=scheduled_at,
    )

    return {
        "publication_id": publication.publication_id,
        "production_id": publication.production_id,
        "schedule_type": "PUBLICATION",
        "scheduled_at": scheduled_at,
        "title": publication.package.title,
  }
