"""
Shadow Files source model.

A source identifies where evidence came from. Source identity is kept
separate from the claim so multiple claims can be traced to the same
source without duplicating source metadata.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class EvidenceSource:
    """Immutable source record."""

    source_id: str
    name: str
    url: Optional[str]
    publisher: Optional[str]
    publication_date: Optional[datetime]
    retrieved_at: datetime

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError(
                "Source ID is required."
            )

        if not self.name.strip():
            raise ValueError(
                "Source name is required."
            )

        if self.retrieved_at.tzinfo is None:
            raise ValueError(
                "Source retrieved_at must be timezone-aware."
            )

        if (
            self.publication_date is not None
            and self.publication_date.tzinfo is None
        ):
            raise ValueError(
                "Source publication_date must be "
                "timezone-aware."
            )


def create_source(
    source_id: str,
    name: str,
    url: Optional[str],
    publisher: Optional[str],
    publication_date: Optional[datetime],
    retrieved_at: datetime,
) -> EvidenceSource:
    """Create a validated evidence source."""

    return EvidenceSource(
        source_id=source_id.strip(),
        name=name.strip(),
        url=url.strip() if url else None,
        publisher=publisher.strip() if publisher else None,
        publication_date=publication_date,
        retrieved_at=retrieved_at,
          )
