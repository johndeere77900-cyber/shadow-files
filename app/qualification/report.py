"""
Qualification report utilities for Shadow Files.
"""

from __future__ import annotations

from app.qualification.models import QualificationReport


def report_summary(report: QualificationReport) -> str:
    """Return a concise human-readable qualification summary."""
    status = "PASSED" if report.passed else "FAILED"

    return (
        f"{status}: "
        f"{report.passed_checks}/{report.total_checks} checks passed; "
        f"{report.failed_checks} failed."
    )


def report_to_dict(report: QualificationReport) -> dict[str, object]:
    """Convert a qualification report into a serializable dictionary."""
    return {
        "run_id": report.run_id,
        "environment": report.environment,
        "started_at": report.started_at.isoformat(),
        "completed_at": report.completed_at.isoformat(),
        "total_checks": report.total_checks,
        "passed_checks": report.passed_checks,
        "failed_checks": report.failed_checks,
        "passed": report.passed,
        "results": [
            {
                "check_id": result.check_id,
                "name": result.name,
                "passed": result.passed,
                "details": result.details,
                "timestamp": result.timestamp.isoformat(),
            }
            for result in report.results
        ],
  }
