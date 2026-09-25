"""
Shadow Files claim repository.

Phase 11 provides persistent storage for factual claims.

Claims are stored separately from evidence so that a single claim
can be supported, disputed, or contextualized by multiple evidence
records.
"""

import sqlite3
from datetime import datetime

from app.evidence.claims import Claim, ClaimStatus


class ClaimRepositoryError(Exception):
    """Raised when a claim repository operation fails."""


class ClaimRepository:
    """Persist and retrieve claim records."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
        self,
        claim: Claim,
    ) -> None:
        """Create a new claim record."""

        try:
            self._connection.execute(
                """
                INSERT INTO claims (
                    claim_id,
                    case_id,
                    statement,
                    status,
                    created_at,
                    reviewed_at,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    claim.claim_id,
                    claim.case_id,
                    claim.statement,
                    claim.status.value,
                    claim.created_at.isoformat(),
                    (
                        claim.reviewed_at.isoformat()
                        if claim.reviewed_at
                        else None
                    ),
                    claim.notes,
                ),
            )
            self._connection.commit()

        except sqlite3.IntegrityError as exc:
            raise ClaimRepositoryError(
                f"Claim '{claim.claim_id}' could not be created."
            ) from exc

    def get(
        self,
        claim_id: str,
    ) -> Claim | None:
        """Retrieve a claim by ID."""

        row = self._connection.execute(
            """
            SELECT
                claim_id,
                case_id,
                statement,
                status,
                created_at,
                reviewed_at,
                notes
            FROM claims
            WHERE claim_id = ?
            """,
            (claim_id,),
        ).fetchone()

        if row is None:
            return None

        reviewed_at = (
            datetime.fromisoformat(row["reviewed_at"])
            if row["reviewed_at"]
            else None
        )

        return Claim(
            claim_id=row["claim_id"],
            case_id=row["case_id"],
            statement=row["statement"],
            status=ClaimStatus(row["status"]),
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            reviewed_at=reviewed_at,
            notes=row["notes"],
        )

    def list_for_case(
        self,
        case_id: str,
    ) -> list[Claim]:
        """Return all claims associated with a case."""

        rows = self._connection.execute(
            """
            SELECT
                claim_id,
                case_id,
                statement,
                status,
                created_at,
                reviewed_at,
                notes
            FROM claims
            WHERE case_id = ?
            ORDER BY created_at ASC
            """,
            (case_id,),
        ).fetchall()

        claims: list[Claim] = []

        for row in rows:
            reviewed_at = (
                datetime.fromisoformat(row["reviewed_at"])
                if row["reviewed_at"]
                else None
            )

            claims.append(
                Claim(
                    claim_id=row["claim_id"],
                    case_id=row["case_id"],
                    statement=row["statement"],
                    status=ClaimStatus(row["status"]),
                    created_at=datetime.fromisoformat(
                        row["created_at"]
                    ),
                    reviewed_at=reviewed_at,
                    notes=row["notes"],
                )
            )

        return claims
