"""
Shadow Files investigation timeline.

Timeline entries preserve dated events discovered during research.
They do not automatically establish that an event is factually
verified; verification remains a separate evidence-review concern.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class TimelineEvent:
    """Immutable event discovered during an investigation."""

    event_id: str
    investigation_id: str
    event_date: datetime
    description: str
    source_id: Optional[str] = None
    certainty: str = "UNKNOWN"
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError(
                "Timeline event ID is required."
            )

        if not self.investigation_id.strip():
            raise ValueError(
                "Investigation ID is required."
            )

        if not self.description.strip():
            raise ValueError(
                "Timeline event description is required."
            )

        if self.event_date.tzinfo is None:
            raise ValueError(
                "Timeline event date must be timezone-aware."
            )

        if not self.certainty.strip():
            raise ValueError(
                "Timeline event certainty is required."
          )
