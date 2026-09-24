"""
Shadow Files job foundation.

Jobs provide a unique identity for operations so that work can be
tracked, audited, retried, and prevented from being confused with
another operation.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class Job:
    """
    Immutable representation of a Shadow Files operation.
    """

    job_id: str
    operation: str
    created_at: str
    status: str = "PENDING"


def create_job(operation: str) -> Job:
    """
    Create a new uniquely identified job.
    """

    if not operation or not operation.strip():
        raise ValueError("Job operation cannot be empty.")

    return Job(
        job_id=str(uuid4()),
        operation=operation.strip(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
