"""
Shadow Files case-memory models.

Phase 11 defines the structured case record used by the application.
Case identity and lifecycle state are kept separate from evidence,
research results, and production records.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Case:
    """Immutable application-level representation of a case."""

    case_id: str
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    summary: str = ""
    location: Optional[str] = None
    case_type: Optional[str] = None
    legal_status: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("Case ID is required.")

        if not self.title.strip():
            raise ValueError("Case title is required.")

        if not isinstance(self.state, str):
            raise TypeError("Case state must be a string.")

        if self.created_at.tzinfo is None:
            raise ValueError(
                "Case created_at must be timezone-aware."
            )

        if self.updated_at.tzinfo is None:
            raise ValueError(
                "Case updated_at must be timezone-aware."
            )

        if self.updated_at < self.created_at:
            raise ValueError(
                "Case updated_at cannot precede created_at."
            )
``
