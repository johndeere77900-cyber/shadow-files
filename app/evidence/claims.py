"""
Shadow Files claim model.

Claims are stored separately from sources so that each factual
statement can be traced to one or more pieces of evidence.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ClaimStatus(str, Enum):
    """Current assessment of a claim."""

    UNREVIEWED = "UNREVIEWED"
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    DISPUTED = "DISPUTED"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class Claim:
    """Immutable claim associated with a case."""

    claim_id: str
    case_id: str
    statement: str
    status: ClaimStatus
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.claim_id.strip():
            raise ValueError(
                "Claim ID is required."
            )

        if not self.case_id.strip():
            raise ValueError(
                "Case ID is required."
            )

        if not self.statement.strip():
            raise ValueError(
                "Claim statement is required."
            )

        if not isinstance(
            self.status,
            ClaimStatus,
        ):
            raise TypeError(
                "Claim status must be a ClaimStatus."
            )

        if self.created_at.tzinfo is None:
            raise ValueError(
                "Claim created_at must be timezone-aware."
            )

        if (
            self.reviewed_at is not None
            and self.reviewed_at.tzinfo is None
        ):
            raise ValueError(
                "Claim reviewed_at must be timezone-aware."
          )
