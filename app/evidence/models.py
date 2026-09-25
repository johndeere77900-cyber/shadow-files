"""
Shadow Files evidence-memory models.

Evidence is stored as a traceable record connected to a case.
The model distinguishes the source, claim, evidence type, and
verification status so later research cannot silently treat every
source or claim as equally established.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EvidenceType(str, Enum):
    """Classification of evidence supporting a claim."""

    OFFICIAL_RECORD = "OFFICIAL_RECORD"
    COURT_RECORD = "COURT_RECORD"
    LAW_ENFORCEMENT = "LAW_ENFORCEMENT"
    CREDIBLE_REPORT = "CREDIBLE_REPORT"
    WITNESS_ACCOUNT = "WITNESS_ACCOUNT"
    INTERVIEW = "INTERVIEW"
    ARCHIVE = "ARCHIVE"
    SECONDARY_SOURCE = "SECONDARY_SOURCE"
    OTHER = "OTHER"


class EvidenceStatus(str, Enum):
    """Verification state of an evidence record."""

    UNREVIEWED = "UNREVIEWED"
    REVIEWED = "REVIEWED"
    VERIFIED = "VERIFIED"
    DISPUTED = "DISPUTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class Evidence:
    """Immutable evidence record."""

    evidence_id: str
    case_id: str
    claim: str
    source_name: str
    source_url: Optional[str]
    evidence_type: EvidenceType
    status: EvidenceStatus
    retrieved_at: datetime
    publication_date: Optional[datetime] = None
    reliability_assessment: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError(
                "Evidence ID is required."
            )

        if not self.case_id.strip():
            raise ValueError(
                "Case ID is required."
            )

        if not self.claim.strip():
            raise ValueError(
                "Evidence claim is required."
            )

        if not self.source_name.strip():
            raise ValueError(
                "Evidence source name is required."
            )

        if not isinstance(
            self.evidence_type,
            EvidenceType,
        ):
            raise TypeError(
                "Evidence type must be an EvidenceType."
            )

        if not isinstance(
            self.status,
            EvidenceStatus,
        ):
            raise TypeError(
                "Evidence status must be an EvidenceStatus."
            )

        if self.retrieved_at.tzinfo is None:
            raise ValueError(
                "Evidence retrieved_at must be timezone-aware."
            )

        if (
            self.publication_date is not None
            and self.publication_date.tzinfo is None
        ):
            raise ValueError(
                "Evidence publication_date must be "
                "timezone-aware."
  )
