"""
Shadow Files audit-event foundation.

Every important system action should eventually produce an immutable
audit event so that the system can explain what happened, when it
happened, who or what initiated it, and what the result was.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass(frozen=True)
class AuditEvent:
    """
    Immutable record of a system action or state change.
    """

    timestamp: str
    event_id: str
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


def new_audit_event(
    *,
    actor: str,
    intent: str,
    command: str,
    target: str,
    result: str,
    previous_state: Optional[str] = None,
    new_state: Optional[str] = None,
    error: Optional[str] = None,
    provider: Optional[str] = None,
    job_id: Optional[str] = None,
) -> AuditEvent:
    """
    Create a new immutable audit event.

    The event ID and timestamp are generated automatically.
    """

    return AuditEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_id=str(uuid4()),
        actor=actor,
        intent=intent,
        command=command,
        target=target,
        previous_state=previous_state,
        new_state=new_state,
        result=result,
        error=error,
        provider=provider,
        job_id=job_id,
    )


def audit_dict(event: AuditEvent) -> dict:
    """
    Convert an audit event into a dictionary suitable for persistence.
    """

    return asdict(event)
