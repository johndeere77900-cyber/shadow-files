"""
Shadow Files Phase 12 investigation repository tests.

These tests verify that investigation records, research sources,
research items, and timeline events persist correctly and maintain
their foreign-key relationships.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.investigation.models import (
    Investigation,
    ResearchItem,
    ResearchItemType,
    ResearchStatus,
)
from app.investigation.repository import (
    InvestigationRepository,
    InvestigationRepositoryError,
)
from app.investigation.sources import ResearchSource
from app.investigation.timeline import TimelineEvent
from database.investigation_schema import create_investigation_schema
from database.migrations import migrate


class InvestigationRepositoryTests(unittest.TestCase):
    """Verify investigation persistence."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

        migrate(self.connection)

        self.connection.execute(
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
                "CASE-001",
                "Repository Test Case",
                "IDEA",
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.connection.commit()

        create_investigation_schema(self.connection)

        self.repository = InvestigationRepository(
            self.connection
        )
        self.now = datetime.now(timezone.utc)

    def tearDown(self) -> None:
        self.connection.close()

    def test_investigation_round_trip(self) -> None:
        investigation = Investigation(
            investigation_id="INV-001",
            case_id="CASE-001",
            status=ResearchStatus.NOT_STARTED,
            started_at=self.now,
            notes="Initial investigation.",
        )

        self.repository.create(investigation)

        stored = self.repository.get("INV-001")

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.investigation_id,
            "INV-001",
        )
        self.assertEqual(
            stored.case_id,
            "CASE-001",
        )
        self.assertEqual(
            stored.status,
            ResearchStatus.NOT_STARTED,
        )
        self.assertEqual(
            stored.notes,
            "Initial investigation.",
        )

    def test_unknown_investigation_returns_none(self) -> None:
        self.assertIsNone(
            self.repository.get("UNKNOWN")
        )

    def test_research_item_round_trip(self) -> None:
        investigation = Investigation(
            investigation_id="INV-002",
            case_id="CASE-001",
            status=ResearchStatus.RESEARCHING,
            started_at=self.now,
        )
        self.repository.create(investigation)

        item = ResearchItem(
            item_id="ITEM-001",
            investigation_id="INV-002",
            item_type=ResearchItemType.FACT,
            statement="A documented event occurred.",
            discovered_at=self.now,
        )

        self.repository.create_item(item)

        stored = self.repository.get_item("ITEM-001")

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.investigation_id,
            "INV-002",
        )
        self.assertEqual(
            stored.item_type,
            ResearchItemType.FACT,
        )

    def test_source_round_trip(self) -> None:
        investigation = Investigation(
            investigation_id="INV-003",
            case_id="CASE-001",
            status=ResearchStatus.RESEARCHING,
            started_at=self.now,
        )
        self.repository.create(investigation)

        source = ResearchSource(
            source_id="RSOURCE-001",
            investigation_id="INV-003",
            name="Example Research Source",
            url="https://example.com",
            publisher="Example Publisher",
            discovered_at=self.now,
        )

        self.repository.create_source(source)

        stored = self.repository.get_source(
            "RSOURCE-001"
        )

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.name,
            "Example Research Source",
        )
        self.assertEqual(
            stored.publisher,
            "Example Publisher",
        )

    def test_timeline_event_round_trip(self) -> None:
        investigation = Investigation(
            investigation_id="INV-004",
            case_id="CASE-001",
            status=ResearchStatus.RESEARCHING,
            started_at=self.now,
        )
        self.repository.create(investigation)

        event = TimelineEvent(
            event_id="EVENT-001",
            investigation_id="INV-004",
            event_date=self.now,
            description="A documented event occurred.",
            certainty="HIGH",
        )

        self.repository.create_timeline_event(event)

        stored = self.repository.get_timeline_event(
            "EVENT-001"
        )

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.investigation_id,
            "INV-004",
        )
        self.assertEqual(
            stored.description,
            "A documented event occurred.",
        )
        self.assertEqual(
            stored.certainty,
            "HIGH",
        )

    def test_unknown_case_cannot_create_investigation(self) -> None:
        investigation = Investigation(
            investigation_id="INV-005",
            case_id="UNKNOWN-CASE",
            status=ResearchStatus.NOT_STARTED,
            started_at=self.now,
        )

        with self.assertRaises(
            InvestigationRepositoryError
        ):
            self.repository.create(investigation)

    def test_unknown_investigation_cannot_create_item(self) -> None:
        item = ResearchItem(
            item_id="ITEM-UNKNOWN",
            investigation_id="UNKNOWN-INV",
            item_type=ResearchItemType.FACT,
            statement="This should not persist.",
            discovered_at=self.now,
        )

        with self.assertRaises(
            InvestigationRepositoryError
        ):
            self.repository.create_item(item)

    def test_case_deletion_cascades_investigation(self) -> None:
        investigation = Investigation(
            investigation_id="INV-DELETE",
            case_id="CASE-001",
            status=ResearchStatus.NOT_STARTED,
            started_at=self.now,
        )
        self.repository.create(investigation)

        self.connection.execute(
            """
            DELETE FROM cases
            WHERE case_id = ?
            """,
            ("CASE-001",),
        )
        self.connection.commit()

        self.assertIsNone(
            self.repository.get("INV-DELETE")
        )


if __name__ == "__main__":
    unittest.main()
