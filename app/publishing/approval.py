"""
Publication approval controls for Shadow Files.

Approval is deliberately separate from production completion.
A completed production is not automatically authorized for publication.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .errors import PublicationApprovalError
from .models import Publication
from .status import PublicationStatus


@dataclass(frozen=True)
class ApprovalRecord:
    """Immutable record of a publication approval decision."""

    publication_id: str
    approved: bool
    approved_by: str
    approved_at: datetime
    note: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.publication_id.strip():
            raise ValueError("publication_id is required")

        if not self.approved_by.strip():
            raise ValueError("approved_by is required")

        if self.approved_at.tzinfo is None:
            raise ValueError("approved_at must be timezone-aware")


def validate_approval(
    publication: Publication,
) -> None:
    """
    Verify that a publication is eligible for approval.
    """

    if publication.status not in {
        PublicationStatus.PENDING_APPROVAL,
        PublicationStatus.PAUSED,
    }:
        raise PublicationApprovalError(
            "Publication must be pending approval before approval "
            f"can be granted; current status is "
            f"{publication.status.value}."
        )


def create_approval_record(
    publication: Publication,
    *,
    approved_by: str,
    note: Optional[str] = None,
) -> ApprovalRecord:
    """
    Create an approval record for a publication.

    This function records approval intent but does not itself change
    the publication state. State changes remain the responsibility of
    the publication service/repository.
    """

    validate_approval(publication)

    if not approved_by.strip():
        raise PublicationApprovalError(
            "approved_by is required."
        )

    return ApprovalRecord(
        publication_id=publication.publication_id,
        approved=True,
        approved_by=approved_by,
        approved_at=datetime.now(timezone.utc),
        note=note,
    )


def require_approved_publication(
    publication: Publication,
) -> None:
    """
    Prevent upload/publication unless explicit approval exists.
    """

    if publication.status != PublicationStatus.APPROVED:
        raise PublicationApprovalError(
            "Publication requires explicit approval before "
            f"external publishing; current status is "
            f"{publication.status.value}."
      )
