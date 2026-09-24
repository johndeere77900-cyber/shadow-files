"""
Shadow Files database models.

These lightweight models represent records stored in the persistent
database. They are deliberately separate from the database connection
and SQL schema layers.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CaseRecord:
    """Persistent representation of a Shadow Files case."""

    case_id: str
    title: str
    state: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class JobRecord:
    """Persistent representation of a Shadow Files job."""

    job_id: str
    operation: str
    status: str
    created_at: str


@dataclass(frozen=True)
class AuditEventRecord:
    """Persistent representation of an audit event."""

    event_id: str
    timestamp: str
    actor: str
    intent: str
    command: str
    target: str

    previous_state: Optional[str]
    new_state: Optional[str]

    result: str

    error: Optional[str] = None
    provider: Optional[str] = None
    job_id: Optional[str] = None
