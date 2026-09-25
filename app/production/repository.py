"""
Shadow Files production repository.

Provides persistent storage operations for production records while
keeping database access outside the production-domain models.
"""

import sqlite3
from datetime import datetime
from typing import Optional

from app.production.models import (
    ContentType,
    Production,
    ProductionStatus,
)


class ProductionRepository:
    """Persistence operations for production records."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def create(self, production: Production) -> None:
        """Create a production record."""

        self._connection.execute(
            """
            INSERT INTO productions (
                production_id,
                case_id,
                investigation_id,
                status,
                title,
                content_type,
                notes,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                production.production_id,
                production.case_id,
                production.investigation_id,
                production.status.value,
                production.title,
                (
                    production.content_type.value
                    if production.content_type is not None
                    else None
                ),
                production.notes,
                production.created_at.isoformat(),
                production.updated_at.isoformat(),
            ),
        )
        self._connection.commit()

    def get(
        self,
        production_id: str,
    ) -> Optional[Production]:
        """Return a production by ID, or None when absent."""

        row = self._connection.execute(
            """
            SELECT
                production_id,
                case_id,
                investigation_id,
                status,
                title,
                content_type,
                notes,
                created_at,
                updated_at
            FROM productions
            WHERE production_id = ?
            """,
            (production_id,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def update_status(
        self,
        production_id: str,
        status: ProductionStatus,
        updated_at: datetime,
    ) -> Production:
        """Update a production status and return the updated record."""

        existing = self.get(production_id)

        if existing is None:
            raise KeyError(
                f"Production not found: {production_id}"
            )

        updated = Production(
            production_id=existing.production_id,
            case_id=existing.case_id,
            investigation_id=existing.investigation_id,
            status=status,
            created_at=existing.created_at,
            updated_at=updated_at,
            title=existing.title,
            content_type=existing.content_type,
            notes=existing.notes,
        )

        self._connection.execute(
            """
            UPDATE productions
            SET status = ?,
                updated_at = ?
            WHERE production_id = ?
            """,
            (
                status.value,
                updated_at.isoformat(),
                production_id,
            ),
        )
        self._connection.commit()

        return updated

    def list_for_case(
        self,
        case_id: str,
    ) -> list[Production]:
        """Return all productions associated with a case."""

        rows = self._connection.execute(
            """
            SELECT
                production_id,
                case_id,
                investigation_id,
                status,
                title,
                content_type,
                notes,
                created_at,
                updated_at
            FROM productions
            WHERE case_id = ?
            ORDER BY created_at ASC
            """,
            (case_id,),
        ).fetchall()

        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(
        row: sqlite3.Row,
    ) -> Production:
        """Convert a database row into a production model."""

        content_type = row["content_type"]

        return Production(
            production_id=row["production_id"],
            case_id=row["case_id"],
            investigation_id=row["investigation_id"],
            status=ProductionStatus(row["status"]),
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            updated_at=datetime.fromisoformat(
                row["updated_at"]
            ),
            title=row["title"],
            content_type=(
                ContentType(content_type)
                if content_type is not None
                else None
            ),
            notes=row["notes"],
      )
