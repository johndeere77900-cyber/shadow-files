"""
Shadow Files Phase 12 end-to-end integration tests.

These tests verify the complete Phase 12 investigation foundation:
database setup, investigation lifecycle, source storage, research
items, timeline events, and separation from verified evidence.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.investigation.models import (
    ResearchItem,
    ResearchItemType,
    ResearchStatus,
)
from app.investigation.repository import InvestigationRepository
from app.investigation.service import InvestigationService
from app.investigation.sources import ResearchSource
from app.investigation.timeline import TimelineEvent
from database.migrations import migrate_investigation_schema
from database.schema import create_schema


class Phase12IntegrationTests(unittest.TestCase):
    """Run the complete Phase 12 investigation foundation."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")

        migrate_investigation_schema(self.connection)

        self.connection.execute(
            """
            INSERT INTO cases (
                case_id,
                title,
                state,
                created_at,
                updated_at,
                summary
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "CASE-PHASE12",
                "Phase 12 Integration Case",
                "IDEA",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
                "",
            ),
        )
        self.connection.commit()

        self.repository = InvestigationRepository(
            self.connection
        )
        self.service = InvestigationService(
            self.connection
        )

    def tearDown(self) -> None:
        self.connection.close()

    def test_complete_investigation_flow(self) -> None:
        started_at = datetime(
            2026,
            1,
            1,
            10,
            0,
            tzinfo=timezone.utc,
        )

        investigation = self.service.create(
            investigation_id="INV-PHASE12",
            case_id="CASE-PHASE12",
            started_at=started_at,
        )

        self.assertEqual(
            investigation.status,
            ResearchStatus.NOT_STARTED,
        )

        investigation = self.service.change_status(
            "INV-PHASE12",
            ResearchStatus.RESEARCHING,
        )

        self.assertEqual(
            investigation.status,
            ResearchStatus.RESEARCHING,
        )

        source = ResearchSource(
            source_id="SRC-PHASE12",
            investigation_id="INV-PHASE12",
            name="Example Research Source",
            url="https://example.com",
            publisher="Example Publisher",
            discovered_at=datetime(
                2026,
                1,
                1,
                11,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.repository.create_source(source)

        item = ResearchItem(
            item_id="ITEM-PHASE12",
            investigation_id="INV-PHASE12",
            item_type=ResearchItemType.FACT,
            statement="A research finding supported by the source.",
            discovered_at=datetime(
                2026,
                1,
                1,
                12,
                0,
                tzinfo=timezone.utc,
            ),
            source_id="SRC-PHASE12",
        )

        self.repository.create_item(item)

        timeline_event = TimelineEvent(
            event_id="EVENT-PHASE12",
            investigation_id="INV-PHASE12",
            event_date=datetime(
                2026,
                1,
                2,
                0,
                0,
                tzinfo=timezone.utc,
            ),
            description="A dated event discovered during research.",
            source_id="SRC-PHASE12",
            certainty="SUPPORTED",
        )

        self.repository.create_timeline_event(
            timeline_event
        )

        investigation = self.service.change_status(
            "INV-PHASE12",
            ResearchStatus.EVIDENCE_REVIEW,
        )

        self.assertEqual(
            investigation.status,
            ResearchStatus.EVIDENCE_REVIEW,
        )

        investigation = self.service.change_status(
            "INV-PHASE12",
            ResearchStatus.VERIFIED,
        )

        self.assertEqual(
            investigation.status,
            ResearchStatus.VERIFIED,
        )

        self.assertIsNotNone(
            investigation.completed_at
        )

        stored_investigation = self.repository.get(
            "INV-PHASE12"
        )
        stored_source = self.repository.get_source(
            "SRC-PHASE12"
        )
        stored_item = self.repository.get_item(
            "ITEM-PHASE12"
        )
        stored_event = (
            self.repository.get_timeline_event(
                "EVENT-PHASE12"
            )
        )

        self.assertIsNotNone(stored_investigation)
        self.assertIsNotNone(stored_source)
        self.assertIsNotNone(stored_item)
        self.assertIsNotNone(stored_event)

        self.assertEqual(
            stored_investigation.status,
            ResearchStatus.VERIFIED,
        )
        self.assertEqual(
            stored_item.source_id,
            "SRC-PHASE12",
        )
        self.assertEqual(
            stored_event.source_id,
            "SRC-PHASE12",
        )

        evidence_count = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM evidence
            WHERE case_id = ?
            """,
            ("CASE-PHASE12",),
        ).fetchone()

        self.assertEqual(
            evidence_count["count"],
            0,
        )

    def test_database_can_be_initialized_from_fresh_connection(
        self,
    ) -> None:
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")

        try:
            create_schema(connection)
            migrate_investigation_schema(connection)

            required_tables = {
                "cases",
                "evidence",
                "claims",
                "evidence_sources",
                "claim_evidence_links",
                "investigations",
                "research_sources",
                "research_items",
                "investigation_timeline",
            }

            rows = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()

            actual_tables = {
                row["name"]
                for row in rows
            }

            self.assertTrue(
                required_tables.issubset(
                    actual_tables
                )
            )
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
