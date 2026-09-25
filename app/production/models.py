"""
Shadow Files production-domain models.

These models represent the controlled transition from verified
investigation results into story, script, scene, and production work.
They do not perform external AI, media, or rendering operations.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ProductionStatus(str, Enum):
    """Lifecycle state for a production package."""

    NOT_STARTED = "NOT_STARTED"
    STORY_PLANNING = "STORY_PLANNING"
    SCRIPT_DRAFT = "SCRIPT_DRAFT"
    SCRIPT_REVIEW = "SCRIPT_REVIEW"
    SCRIPT_APPROVED = "SCRIPT_APPROVED"
    SCENE_PLANNING = "SCENE_PLANNING"
    PRODUCTION = "PRODUCTION"
    QC = "QC"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    READY = "READY"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"


class ContentType(str, Enum):
    """Types of production content."""

    STORY = "STORY"
    SCRIPT = "SCRIPT"
    SCENE_PLAN = "SCENE_PLAN"


@dataclass(frozen=True)
class Production:
    """Immutable application-level production record."""

    production_id: str
    case_id: str
    investigation_id: str
    status: ProductionStatus
    created_at: datetime
    updated_at: datetime
    title: Optional[str] = None
    content_type: Optional[ContentType] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.production_id.strip():
            raise ValueError("Production ID is required.")

        if not self.case_id.strip():
            raise ValueError("Case ID is required.")

        if not self.investigation_id.strip():
            raise ValueError(
                "Investigation ID is required."
            )

        if not isinstance(
            self.status,
            ProductionStatus,
        ):
            raise TypeError(
                "Production status must be a ProductionStatus."
            )

        if self.created_at.tzinfo is None:
            raise ValueError(
                "Production created_at must be timezone-aware."
            )

        if self.updated_at.tzinfo is None:
            raise ValueError(
                "Production updated_at must be timezone-aware."
            )

        if self.updated_at < self.created_at:
            raise ValueError(
                "Production updated_at cannot precede created_at."
            )

        if self.title is not None and not self.title.strip():
            raise ValueError(
                "Production title cannot be blank."
            )

        if self.content_type is not None and not isinstance(
            self.content_type,
            ContentType,
        ):
            raise TypeError(
                "Content type must be a ContentType."
  )
