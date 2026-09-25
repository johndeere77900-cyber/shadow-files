"""
Data models used by the Phase 16 qualification infrastructure.

These models describe qualification results and test evidence. They do
not control the operational Shadow Files workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class QualificationResult:
    """Represents the outcome of one qualification check."""

    check_id: str
    name: str
    passed: bool
    details: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.check_id.strip():
            raise ValueError("check_id must not be empty")

        if not self.name.strip():
            raise ValueError("name must not be empty")

        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")


@dataclass(frozen=True)
class QualificationReport:
    """Aggregated result of a qualification run."""

    run_id: str
    results: tuple[QualificationResult, ...]
    started_at: datetime
    completed_at: datetime
    environment: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.run_id.strip():
            raise ValueError("run_id must not be empty")

        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("started_at must be timezone-aware")

        if (
            self.completed_at.tzinfo is None
            or self.completed_at.utcoffset() is None
        ):
            raise ValueError("completed_at must be timezone-aware")

        if self.completed_at < self.started_at:
            raise ValueError("completed_at cannot be earlier than started_at")

    @property
    def total_checks(self) -> int:
        """Return the number of qualification checks."""
        return len(self.results)

    @property
    def passed_checks(self) -> int:
        """Return the number of successful checks."""
        return sum(result.passed for result in self.results)

    @property
    def failed_checks(self) -> int:
        """Return the number of failed checks."""
        return sum(not result.passed for result in self.results)

    @property
    def passed(self) -> bool:
        """Return True only when every qualification check passed."""
        return self.total_checks > 0 and self.failed_checks == 0
