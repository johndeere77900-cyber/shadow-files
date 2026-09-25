"""
Shadow Files source repository.

Phase 11 provides persistent storage for evidence sources.

Sources are stored independently from claims and evidence records so
multiple claims can reference the same source without duplicating
source metadata.
"""

import sqlite3
from datetime import datetime

from app.evidence.source import EvidenceSource


class SourceRepositoryError(Exception):
    """Raised when a source repository operation fails."""


class SourceRepository:
    """Persist and retrieve evidence source records."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
        self,
        source: EvidenceSource,
    ) -> None:
        """Create a new source record."""

        try:
            self._connection.execute(
                """
                INSERT INTO evidence_sources (
                    source_id,
                    name,
                    url,
                    publisher,
                    publication_date,
                    retrieved_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    source.source_id,
                    source.name,
                    source.url,
                    source.publisher,
                    (
                        source.publication_date.isoformat()
                        if source.publication_date
                        else None
                    ),
                    source.retrieved_at.isoformat(),
                ),
            )
            self._connection.commit()

        except sqlite3.IntegrityError as exc:
            raise SourceRepositoryError(
                f"Source '{source.source_id}' could not be created."
            ) from exc

    def get(
        self,
        source_id: str,
    ) -> EvidenceSource | None:
        """Retrieve a source by ID."""

        row = self._connection.execute(
            """
            SELECT
                source_id,
                name,
                url,
                publisher,
                publication_date,
                retrieved_at
            FROM evidence_sources
            WHERE source_id = ?
            """,
            (source_id,),
        ).fetchone()

        if row is None:
            return None

        publication_date = (
            datetime.fromisoformat(row["publication_date"])
            if row["publication_date"]
            else None
        )

        return EvidenceSource(
            source_id=row["source_id"],
            name=row["name"],
            url=row["url"],
            publisher=row["publisher"],
            publication_date=publication_date,
            retrieved_at=datetime.fromisoformat(
                row["retrieved_at"]
            ),
        )

    def list_all(self) -> list[EvidenceSource]:
        """Return all stored evidence sources."""

        rows = self._connection.execute(
            """
            SELECT
                source_id,
                name,
                url,
                publisher,
                publication_date,
                retrieved_at
            FROM evidence_sources
            ORDER BY retrieved_at ASC
            """
        ).fetchall()

        sources: list[EvidenceSource] = []

        for row in rows:
            publication_date = (
                datetime.fromisoformat(
                    row["publication_date"]
                )
                if row["publication_date"]
                else None
            )

            sources.append(
                EvidenceSource(
                    source_id=row["source_id"],
                    name=row["name"],
                    url=row["url"],
                    publisher=row["publisher"],
                    publication_date=publication_date,
                    retrieved_at=datetime.fromisoformat(
                        row["retrieved_at"]
                    ),
                )
            )

        return sources
