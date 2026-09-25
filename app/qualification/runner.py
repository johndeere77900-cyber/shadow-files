"""
Qualification runner for the Shadow Files final audit infrastructure.

The runner executes registered qualification checks and produces a
structured report. It does not determine production readiness on its
own; the final audit interprets the collected evidence.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from uuid import uuid4

from app.qualification.errors import QualificationExecutionError
from app.qualification.models import QualificationReport, QualificationResult

QualificationCheck = Callable[[], QualificationResult]


class QualificationRunner:
    """Execute a deterministic collection of qualification checks."""

    def __init__(
        self,
        checks: Iterable[QualificationCheck] = (),
    ) -> None:
        self._checks = tuple(checks)

    @property
    def checks(self) -> tuple[QualificationCheck, ...]:
        """Return the registered checks."""
        return self._checks

    def run(
        self,
        *,
        environment: str | None = None,
    ) -> QualificationReport:
        """Execute all registered checks and return a qualification report."""
        started_at = datetime.now(timezone.utc)
        results: list[QualificationResult] = []

        for check in self._checks:
            try:
                result = check()
            except Exception as exc:
                raise QualificationExecutionError(
                    f"Qualification check failed to execute: {exc}"
                ) from exc

            if not isinstance(result, QualificationResult):
                raise QualificationExecutionError(
                    "Qualification checks must return QualificationResult."
                )

            results.append(result)

        completed_at = datetime.now(timezone.utc)

        return QualificationReport(
            run_id=str(uuid4()),
            results=tuple(results),
            started_at=started_at,
            completed_at=completed_at,
            environment=environment,
              )
