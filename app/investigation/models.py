"""
Shadow Files investigation models.

Phase 12 defines the structured objects used by the investigation
engine. Research results remain separate from verified claims and
production content until they pass the appropriate review process.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ResearchStatus(str, Enum):
    """Lifecycle status of an investigation."""

    NOT_STARTED = "NOT_STARTED"
    RESEARCHING = "RESEARCHING"
    EVIDENCE_REVIEW = "EVIDENCE_REVIEW"
    VERIFIED = "VERIFIED"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"


class ResearchItemType(str, Enum):
    """Classification of information discovered during research."""

    FACT = "FACT"
    CLAIM = "CLAIM"
    ALLEGATION = "ALLEGATION"
    WITNESS_ACCOUNT = "WITNESS_ACCOUNT"
    OFFICIAL_STATEMENT = "OFFICIAL_STATEMENT"
    THEORY = "THEORY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Investigation:
    """Immutable investigation record."""

    investigation_id: str
    case_id: str
    status: ResearchStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.investigation_id.strip():
            raise ValueError(
                "Investigation ID is required."
            )

        if not self.case_id.strip():
            raise ValueError(
                "Case ID is required."
            )

        if not isinstance(
            self.status,
            ResearchStatus,
        ):
            raise TypeError(
                "Investigation status must be a ResearchStatus."
            )

        if self.started_at.tzinfo is None:
            raise ValueError(
                "Investigation started_at must be timezone-aware."
            )

        if (
            self.completed_at is not None
            and self.completed_at.tzinfo is None
        ):
            raise ValueError(
                "Investigation completed_at must be timezone-aware."
            )

        if (
            self.completed_at is not None
            and self.completed_at < self.started_at
        ):
            raise ValueError(
                "Investigation completed_at cannot precede started_at."
            )


@dataclass(frozen=True)
class ResearchItem:
    """Immutable item discovered during an investigation."""

    item_id: str
    investigation_id: str
    item_type: ResearchItemType
    statement: str
    discovered_at: datetime
    source_id: Optional[str] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.item_id.strip():
            raise ValueError(
                "Research item ID is required."
            )

        if not self.investigation_id.strip():
            raise ValueError(
                "Investigation ID is required."
            )

        if not isinstance(
            self.item_type,
            ResearchItemType,
        ):
            raise TypeError(
                "Research item type must be a ResearchItemType."
            )

        if not self.statement.strip():
            raise ValueError(
                "Research item statement is required."
            )

        if self.discovered_at.tzinfo is None:
            raise ValueError(
                "Research item discovered_at must be timezone-aware."
  )
