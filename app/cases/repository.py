"""
Shadow Files case repository.

Phase 11 provides the persistence boundary for case records.

The repository uses the existing Phase 7 database layer rather than
creating a second storage system.
"""

from dataclasses import asdict
from datetime import datetime
import sqlite3

from app.cases.models import Case


class CaseRepositoryError(Exception):
    """Raised when a case repository operation fails."""


class CaseRepository:
    """Persist and retrieve case records."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
        self,
        case: Case,
    ) -> None:
        """Create a new case record."""

        try:
            self._connection.execute(
                """
                INSERT INTO cases (
                    case_id,
                    title,
                    state,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    case.case_id,
                    case.title,
                    case.state,
                    case.created_at.isoformat(),
                    case.updated_at.isoformat(),
                ),
            )
            self._connection.commit()

        except sqlite3.IntegrityError as exc:
            raise CaseRepositoryError(
                f"Case '{case.case_id}' could not be created."
            ) from exc

    def get(
        self,
        case_id: str,
    ) -> Case | None:
        """Retrieve a case by ID."""

        row = self._connection.execute(
            """
            SELECT
                case_id,
                title,
                state,
                created_at,
                updated_at
            FROM cases
            WHERE case_id = ?
            """,
            (case_id,),
        ).fetchone()

        if row is None:
            return None

        return Case(
            case_id=row["case_id"],
            title=row["title"],
            state=row["state"],
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            updated_at=datetime.fromisoformat(
                row["updated_at"]
            ),
            )
