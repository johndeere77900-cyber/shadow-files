"""
Shadow Files Phase 12 integration tests.

These tests verify that the investigation layer integrates with the
existing case database and preserves the separation between research
records and verified case evidence.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.investigation.models import (
    ResearchItemType,
    ResearchStatus,
)
from app.investigation.service import InvestigationService
from database.investigation_schema import (
    create_investigation_schema,
)
from database.schema import create_schema


class Phase12IntegrationTests(unittest.TestCase):
    """Validate the integrated Phase 12 investigation workflow."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")

        create_schema(self.connection)
        create_investigation_schema(self.connection)

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
                "CASE-P12",
                "Phase 12 Integration Case",
                "IDEA",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
            ),
        )
        self.connection.commit()

        self.service = InvestigationService(
            self.connection
        )

    def tearDown(self) -> None:
        self.connection.close()

    def test_investigation_can_be_created_for_existing_case(
        self,
    ) -> None:
        investigation = self.service.create(
            investigation_id="INV-P12",
            case_id="CASE-P12",
            started_at=datetime.now(timezone.utc),
        )

        self.assertEqual(
            investigation.investigation_id,
            "INV-P12",
        )
        self.assertEqual(
            investigation.case_id,
            "CASE-P12",
        )
        self.assertEqual(
            investigation.status,
            ResearchStatus.NOT_STARTED,
        )

    def test_research_record_remains_separate_from_case_evidence(
        self,
    ) -> None:
        self.service.create(
            investigation_id="INV-SEPARATION",
            case_id="CASE-P12",
            started_at=datetime.now(timezone.utc),
        )

        self.connection.execute(
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
                "ITEM-P12",
                "INV-SEPARATION",
                ResearchItemType.FACT.value,
                "Research discovery.",
                "2026-01-01T02:00:00+00:00",
                None,
                "",
            ),
        )
        self.connection.commit()

        research_row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM research_items
            WHERE investigation_id = ?
            """,
            ("INV-SEPARATION",),
        ).fetchone()

        evidence_row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM evidence
            WHERE case_id = ?
            """,
            ("CASE-P12",),
        ).fetchone()

        self.assertEqual(
            research_row["count"],
            1,
        )
        self.assertEqual(
            evidence_row["count"],
            0,
        )

    def test_investigation_reaches_verified_state_through_review(
        self,
    ) -> None:
        self.service.create(
            investigation_id="INV-VERIFIED",
            case_id="CASE-P12",
            started_at=datetime.now(timezone.utc),
        )

        self.service.change_status(
            "INV-VERIFIED",
            ResearchStatus.RESEARCHING,
        )

        self.service.change_status(
            "INV-VERIFIED",
            ResearchStatus.EVIDENCE_REVIEW,
        )

        investigation = self.service.change_status(
            "INV-VERIFIED",
            ResearchStatus.VERIFIED,
        )

        self.assertEqual(
            investigation.status,
            ResearchStatus.VERIFIED,
        )
        self.assertIsNotNone(
            investigation.completed_at,
        )


if __name__ == "__main__":
    unittest.main()
