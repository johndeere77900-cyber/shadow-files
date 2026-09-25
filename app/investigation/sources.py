"""
Shadow Files investigation source handling.

Research sources are represented explicitly so the investigation
engine can preserve provenance and distinguish source discovery from
claim verification.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class SourceValidationError(Exception):
    """Raised when a research source is invalid."""


@dataclass(frozen=True)
class ResearchSource:
    """Immutable source discovered during an investigation."""

    source_id: str
    investigation_id: str
    name: str
    url: Optional[str]
    publisher: Optional[str]
    discovered_at: datetime

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise SourceValidationError(
                "Source ID is required."
            )

        if not self.investigation_id.strip():
            raise SourceValidationError(
                "Investigation ID is required."
            )

        if not self.name.strip():
            raise SourceValidationError(
                "Source name is required."
            )

        if self.discovered_at.tzinfo is None:
            raise SourceValidationError(
                "Source discovered_at must be timezone-aware."
            )

        if self.url is not None and not self.url.strip():
            raise SourceValidationError(
                "Source URL cannot be empty when provided."
            )

        if (
            self.publisher is not None
            and not self.publisher.strip()
        ):
            raise SourceValidationError(
                "Source publisher cannot be empty when provided."
            )


def create_research_source(
    source_id: str,
    investigation_id: str,
    name: str,
    url: Optional[str],
    publisher: Optional[str],
    discovered_at: datetime,
) -> ResearchSource:
    """Create a validated research source."""

    return ResearchSource(
        source_id=source_id.strip(),
        investigation_id=investigation_id.strip(),
        name=name.strip(),
        url=url.strip() if url else None,
        publisher=publisher.strip() if publisher else None,
        discovered_at=discovered_at,
      )
