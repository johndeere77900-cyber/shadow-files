"""
Shadow Files investigation repository.

Phase 12 provides the persistence boundary for investigation records,
research items, sources, and timeline events.

The repository uses the existing SQLite database connection and does
not create a second storage system.
"""

import sqlite3
from datetime import datetime
from typing import Optional

from app.investigation.models import (
    Investigation,
    ResearchItem,
    ResearchItemType,
    ResearchStatus,
)
from app.investigation.sources import ResearchSource
from app.investigation.timeline import TimelineEvent


class InvestigationRepositoryError(Exception):
    """Raised when an investigation repository operation fails."""


class InvestigationRepository:
    """Persist and retrieve investigation records."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
        self,
        investigation: Investigation,
    ) -> None:
        """Create an investigation record."""

        try:
            self._connection.execute(
                """
                INSERT INTO investigations (
                    investigation_id,
                    case_id,
                    status,
                    started_at,
                    completed_at,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    investigation.investigation_id,
                    investigation.case_id,
                    investigation.status.value,
                    investigation.started_at.isoformat(),
                    (
                        investigation.completed_at.isoformat()
                        if investigation.completed_at
                        else None
                    ),
                    investigation.notes,
                ),
            )
            self._connection.commit()

        except sqlite3.IntegrityError as exc:
            raise InvestigationRepositoryError(
                f"Investigation "
                f"'{investigation.investigation_id}' "
                "could not be created."
            ) from exc

    def get(
        self,
        investigation_id: str,
    ) -> Optional[Investigation]:
        """Retrieve an investigation by ID."""

        row = self._connection.execute(
            """
            SELECT
                investigation_id,
                case_id,
                status,
                started_at,
                completed_at,
                notes
            FROM investigations
            WHERE investigation_id = ?
            """,
            (investigation_id,),
        ).fetchone()

        if row is None:
            return None

        completed_at = (
            datetime.fromisoformat(row["completed_at"])
            if row["completed_at"]
            else None
        )

        return Investigation(
            investigation_id=row["investigation_id"],
            case_id=row["case_id"],
            status=ResearchStatus(row["status"]),
            started_at=datetime.fromisoformat(
                row["started_at"]
            ),
            completed_at=completed_at,
            notes=row["notes"],
        )

    def create_item(
        self,
        item: ResearchItem,
    ) -> None:
        """Create a research item."""

        try:
            self._connection.execute(
                """
                INSERT INTO research_items (
                    item_id,
                    investigation_id,
                    item_type,
                    statement,
                    discovered_at,
                    source_id,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.item_id,
                    item.investigation_id,
                    item.item_type.value,
                    item.statement,
                    item.discovered_at.isoformat(),
                    item.source_id,
                    item.notes,
                ),
            )
            self._connection.commit()

        except sqlite3.IntegrityError as exc:
            raise InvestigationRepositoryError(
                f"Research item '{item.item_id}' "
                "could not be created."
            ) from exc

    def get_item(
        self,
        item_id: str,
    ) -> Optional[ResearchItem]:
        """Retrieve a research item by ID."""

        row = self._connection.execute(
            """
            SELECT
                item_id,
                investigation_id,
                item_type,
                statement,
                discovered_at,
                source_id,
                notes
            FROM research_items
            WHERE item_id = ?
            """,
            (item_id,),
        ).fetchone()

        if row is None:
            return None

        return ResearchItem(
            item_id=row["item_id"],
            investigation_id=row["investigation_id"],
            item_type=ResearchItemType(row["item_type"]),
            statement=row["statement"],
            discovered_at=datetime.fromisoformat(
                row["discovered_at"]
            ),
            source_id=row["source_id"],
            notes=row["notes"],
        )

    def create_source(
        self,
        source: ResearchSource,
    ) -> None:
        """Create a research source."""

        try:
            self._connection.execute(
                """
                INSERT INTO research_sources (
                    source_id,
                    investigation_id,
                    name,
                    url,
                    publisher,
                    discovered_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    source.source_id,
                    source.investigation_id,
                    source.name,
                    source.url,
                    source.publisher,
                    source.discovered_at.isoformat(),
                ),
            )
            self._connection.commit()

        except sqlite3.IntegrityError as exc:
            raise InvestigationRepositoryError(
                f"Research source '{source.source_id}' "
                "could not be created."
            ) from exc

    def get_source(
        self,
        source_id: str,
    ) -> Optional[ResearchSource]:
        """Retrieve a research source by ID."""

        row = self._connection.execute(
            """
            SELECT
                source_id,
                investigation_id,
                name,
                url,
                publisher,
                discovered_at
            FROM research_sources
            WHERE source_id = ?
            """,
            (source_id,),
        ).fetchone()

        if row is None:
            return None

        return ResearchSource(
            source_id=row["source_id"],
            investigation_id=row["investigation_id"],
            name=row["name"],
            url=row["url"],
            publisher=row["publisher"],
            discovered_at=datetime.fromisoformat(
                row["discovered_at"]
            ),
        )

    def create_timeline_event(
        self,
        event: TimelineEvent,
    ) -> None:
        """Create a timeline event."""

        try:
            self._connection.execute(
                """
                INSERT INTO investigation_timeline (
                    event_id,
                    investigation_id,
                    event_date,
                    description,
                    source_id,
                    certainty,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.investigation_id,
                    event.event_date.isoformat(),
                    event.description,
                    event.source_id,
                    event.certainty,
                    event.notes,
                ),
            )
            self._connection.commit()

        except sqlite3.IntegrityError as exc:
            raise InvestigationRepositoryError(
                f"Timeline event '{event.event_id}' "
                "could not be created."
            ) from exc

    def get_timeline_event(
        self,
        event_id: str,
    ) -> Optional[TimelineEvent]:
        """Retrieve a timeline event by ID."""

        row = self._connection.execute(
            """
            SELECT
                event_id,
                investigation_id,
                event_date,
                description,
                source_id,
                certainty,
                notes
            FROM investigation_timeline
            WHERE event_id = ?
            """,
            (event_id,),
        ).fetchone()

        if row is None:
            return None

        return TimelineEvent(
            event_id=row["event_id"],
            investigation_id=row["investigation_id"],
            event_date=datetime.fromisoformat(
                row["event_date"]
            ),
            description=row["description"],
            source_id=row["source_id"],
            certainty=row["certainty"],
            notes=row["notes"],
    )
