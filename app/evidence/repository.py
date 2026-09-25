"""
Shadow Files evidence repository.

Phase 11 provides the persistence boundary for evidence records.

The repository uses the existing database connection and keeps
evidence storage separate from case-management logic.
"""

import sqlite3
from datetime import datetime

from app.evidence.models import (
    Evidence,
    EvidenceStatus,
    EvidenceType,
)


class EvidenceRepositoryError(Exception):
    """Raised when an evidence repository operation fails."""


class EvidenceRepository:
    """Persist and retrieve evidence records."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
        self,
        evidence: Evidence,
    ) -> None:
        """Create a new evidence record."""

        try:
            self._connection.execute(
                """
                INSERT INTO evidence (
                    evidence_id,
                    case_id,
                    claim,
                    source_name,
                    source_url,
                    evidence_type,
                    status,
                    retrieved_at,
                    publication_date,
                    reliability_assessment,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence.evidence_id,
                    evidence.case_id,
                    evidence.claim,
                    evidence.source_name,
                    evidence.source_url,
                    evidence.evidence_type.value,
                    evidence.status.value,
                    evidence.retrieved_at.isoformat(),
                    (
                        evidence.publication_date.isoformat()
                        if evidence.publication_date
                        else None
                    ),
                    evidence.reliability_assessment,
                    evidence.notes,
                ),
            )
            self._connection.commit()

        except sqlite3.IntegrityError as exc:
            raise EvidenceRepositoryError(
                f"Evidence '{evidence.evidence_id}' "
                "could not be created."
            ) from exc

    def get(
        self,
        evidence_id: str,
    ) -> Evidence | None:
        """Retrieve an evidence record by ID."""

        row = self._connection.execute(
            """
            SELECT
                evidence_id,
                case_id,
                claim,
                source_name,
                source_url,
                evidence_type,
                status,
                retrieved_at,
                publication_date,
                reliability_assessment,
                notes
            FROM evidence
            WHERE evidence_id = ?
            """,
            (evidence_id,),
        ).fetchone()

        if row is None:
            return None

        publication_date = (
            datetime.fromisoformat(
                row["publication_date"]
            )
            if row["publication_date"]
            else None
        )

        return Evidence(
            evidence_id=row["evidence_id"],
            case_id=row["case_id"],
            claim=row["claim"],
            source_name=row["source_name"],
            source_url=row["source_url"],
            evidence_type=EvidenceType(
                row["evidence_type"]
            ),
            status=EvidenceStatus(
                row["status"]
            ),
            retrieved_at=datetime.fromisoformat(
                row["retrieved_at"]
            ),
            publication_date=publication_date,
            reliability_assessment=(
                row["reliability_assessment"]
            ),
            notes=row["notes"],
        )

    def list_for_case(
        self,
        case_id: str,
    ) -> list[Evidence]:
        """Return all evidence records associated with a case."""

        rows = self._connection.execute(
            """
            SELECT
                evidence_id,
                case_id,
                claim,
                source_name,
                source_url,
                evidence_type,
                status,
                retrieved_at,
                publication_date,
                reliability_assessment,
                notes
            FROM evidence
            WHERE case_id = ?
            ORDER BY retrieved_at ASC
            """,
            (case_id,),
        ).fetchall()

        return [
            self.get(row["evidence_id"])
            for row in rows
              ]
