"""
Shadow Files Phase 12 investigation integration qualification tests.

This verifies the complete investigation chain:

Case
  -> Investigation
  -> Research Source
  -> Research Item
  -> Timeline Event

It also verifies that research remains separate from the existing
case/evidence memory while maintaining the required relationships.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.cases.models import Case
from app.cases.repository import CaseRepository
from app.investigation.models import (
    Investigation,
    ResearchItem,
    ResearchItemType,
    ResearchStatus,
)
from app.investigation.repository import InvestigationRepository
from app.investigation.sources import ResearchSource
from app.investigation.timeline import TimelineEvent
from database.investigation_schema import create_investigation_schema
from database.migrations import migrate


class InvestigationIntegrationTests(unittest.TestCase):
    """Verify the complete Phase 12 investigation chain."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

        migrate(self.connection)
        create_investigation_schema(self.connection)

        self.now = datetime.now(timezone.utc)

    def tearDown(self) -> None:
        self.connection.close()

    def test_complete_investigation_chain(self) -> None:
        case_repository = CaseRepository(self.connection)
        investigation_repository = InvestigationRepository(
            self.connection
        )

        case = Case(
            case_id="CASE-001",
            title="Integration Test Case",
            state="IDEA",
            created_at=self.now,
            updated_at=self.now,
        )

        case_repository.create(case)

        investigation = Investigation(
            investigation_id="INV-001",
            case_id="CASE-001",
            status=ResearchStatus.RESEARCHING,
            started_at=self.now,
            notes="Phase 12 integration investigation.",
        )

        investigation_repository.create(investigation)

        source = ResearchSource(
            source_id="RSOURCE-001",
            investigation_id="INV-001",
            name="Example Research Source",
            url="https://example.com/source",
            publisher="Example Publisher",
            discovered_at=self.now,
        )

        investigation_repository.create_source(source)

        item = ResearchItem(
            item_id="ITEM-001",
            investigation_id="INV-001",
            item_type=ResearchItemType.FACT,
            statement="A documented event was reported.",
            discovered_at=self.now,
            source_id="RSOURCE-001",
        )

        investigation_repository.create_item(item)

        timeline_event = TimelineEvent(
            event_id="EVENT-001",
            investigation_id="INV-001",
            event_date=self.now,
            description="The documented event occurred.",
            source_id="RSOURCE-001",
            certainty="HIGH",
        )

        investigation_repository.create_timeline_event(
            timeline_event
        )

        stored_investigation = investigation_repository.get(
            "INV-001"
        )
        stored_source = investigation_repository.get_source(
            "RSOURCE-001"
        )
        stored_item = investigation_repository.get_item(
            "ITEM-001"
        )
        stored_event = investigation_repository.get_timeline_event(
            "EVENT-001"
        )

        self.assertIsNotNone(stored_investigation)
        self.assertIsNotNone(stored_source)
        self.assertIsNotNone(stored_item)
        self.assertIsNotNone(stored_event)

        self.assertEqual(
            stored_investigation.case_id,
            case.case_id,
        )

        self.assertEqual(
            stored_source.investigation_id,
            stored_investigation.investigation_id,
        )

        self.assertEqual(
            stored_item.investigation_id,
            stored_investigation.investigation_id,
        )

        self.assertEqual(
            stored_item.source_id,
            stored_source.source_id,
        )

        self.assertEqual(
            stored_event.investigation_id,
            stored_investigation.investigation_id,
        )

        self.assertEqual(
            stored_event.source_id,
            stored_source.source_id,
        )

    def test_investigation_tables_are_separate_from_case_memory(
        self,
    ) -> None:
        tables = {
            row["name"]
            for row in self.connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        self.assertIn("cases", tables)
        self.assertIn("evidence", tables)
        self.assertIn("claims", tables)

        self.assertIn(
            "investigations",
            tables,
        )
        self.assertIn(
            "research_sources",
            tables,
        )
        self.assertIn(
            "research_items",
            tables,
        )
        self.assertIn(
            "investigation_timeline",
            tables,
        )

    def test_case_deletion_removes_investigation_research(
        self,
    ) -> None:
        case_repository = CaseRepository(self.connection)
        investigation_repository = InvestigationRepository(
            self.connection
        )

        case_repository.create(
            Case(
                case_id="CASE-DELETE",
                title="Delete Integration Case",
                state="IDEA",
                created_at=self.now,
                updated_at=self.now,
            )
        )

        investigation_repository.create(
            Investigation(
                investigation_id="INV-DELETE",
                case_id="CASE-DELETE",
                status=ResearchStatus.RESEARCHING,
                started_at=self.now,
            )
        )

        investigation_repository.create_source(
            ResearchSource(
                source_id="RSOURCE-DELETE",
                investigation_id="INV-DELETE",
                name="Deletion Test Source",
                url=None,
                publisher=None,
                discovered_at=self.now,
            )
        )

        investigation_repository.create_item(
            ResearchItem(
                item_id="ITEM-DELETE",
                investigation_id="INV-DELETE",
                item_type=ResearchItemType.CLAIM,
                statement="Deletion test research item.",
                discovered_at=self.now,
                source_id="RSOURCE-DELETE",
            )
        )

        investigation_repository.create_timeline_event(
            TimelineEvent(
                event_id="EVENT-DELETE",
                investigation_id="INV-DELETE",
                event_date=self.now,
                description="Deletion test event.",
                source_id="RSOURCE-DELETE",
                certainty="UNKNOWN",
            )
        )

        self.connection.execute(
            """
            DELETE FROM cases
            WHERE case_id = ?
            """,
            ("CASE-DELETE",),
        )
        self.connection.commit()

        for table, record_id, column in (
            (
                "investigations",
                "INV-DELETE",
                "investigation_id",
            ),
            (
                "research_sources",
                "RSOURCE-DELETE",
                "source_id",
            ),
            (
                "research_items",
                "ITEM-DELETE",
                "item_id",
            ),
            (
                "investigation_timeline",
                "EVENT-DELETE",
                "event_id",
            ),
        ):
            row = self.connection.execute(
                f"""
                SELECT {column}
                FROM {table}
                WHERE {column} = ?
                """,
                (record_id,),
            ).fetchone()

            self.assertIsNone(row)


if __name__ == "__main__":
    unittest.main()
