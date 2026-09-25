"""
Shadow Files claim-evidence links.

This module creates the explicit relationship between a claim and
the evidence supporting, disputing, or contextualizing it.
"""

from dataclasses import dataclass
from enum import Enum


class EvidenceRelation(str, Enum):
    """How evidence relates to a claim."""

    SUPPORTS = "SUPPORTS"
    DISPUTES = "DISPUTES"
    CONTEXTUALIZES = "CONTEXTUALIZES"


@dataclass(frozen=True)
class ClaimEvidenceLink:
    """Immutable relationship between a claim and evidence."""

    link_id: str
    claim_id: str
    evidence_id: str
    relation: EvidenceRelation
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.link_id.strip():
            raise ValueError(
                "Link ID is required."
            )

        if not self.claim_id.strip():
            raise ValueError(
                "Claim ID is required."
            )

        if not self.evidence_id.strip():
            raise ValueError(
                "Evidence ID is required."
            )

        if not isinstance(
            self.relation,
            EvidenceRelation,
        ):
            raise TypeError(
                "Evidence relation must be an EvidenceRelation."
        )
