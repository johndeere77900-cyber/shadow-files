"""
Shadow Files investigation service.

The service coordinates investigation lifecycle operations while
keeping state transitions explicit and preventing unverified research
from being treated as verified automatically.
"""

import sqlite3
from datetime import datetime
from typing import Optional

from app.investigation.models import (
    Investigation,
    ResearchStatus,
)
from app.investigation.repository import InvestigationRepository
from app.investigation.status import transition


class InvestigationService:
    """Application service for investigation lifecycle operations."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._repository = InvestigationRepository(connection)

    def create(
        self,
        investigation_id: str,
        case_id: str,
        started_at: datetime,
        notes: str = "",
    ) -> Investigation:
        """Create a new investigation in NOT_STARTED state."""

        investigation = Investigation(
            investigation_id=investigation_id,
            case_id=case_id,
            status=ResearchStatus.NOT_STARTED,
            started_at=started_at,
            notes=notes,
        )

        self._repository.create(investigation)
        return investigation

    def get(
        self,
        investigation_id: str,
    ) -> Optional[Investigation]:
        """Retrieve an investigation."""

        return self._repository.get(investigation_id)

    def change_status(
        self,
        investigation_id: str,
        target: ResearchStatus,
    ) -> Investigation:
        """Move an investigation through a validated state transition."""

        current = self._repository.get(investigation_id)

        if current is None:
            raise KeyError(
                f"Investigation '{investigation_id}' does not exist."
            )

        new_status = transition(
            current.status,
            target,
        )

        completed_at = current.completed_at

        if new_status == ResearchStatus.VERIFIED:
            completed_at = datetime.now(
                current.started_at.tzinfo
            )

        updated = Investigation(
            investigation_id=current.investigation_id,
            case_id=current.case_id,
            status=new_status,
            started_at=current.started_at,
            completed_at=completed_at,
            notes=current.notes,
        )

        self._repository._connection.execute(
            """
            UPDATE investigations
            SET status = ?, completed_at = ?
            WHERE investigation_id = ?
            """,
            (
                updated.status.value,
                (
                    updated.completed_at.isoformat()
                    if updated.completed_at
                    else None
                ),
                updated.investigation_id,
            ),
        )
        self._repository._connection.commit()

        return updated
