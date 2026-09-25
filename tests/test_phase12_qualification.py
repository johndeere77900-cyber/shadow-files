"""
Shadow Files Phase 12 qualification tests.

These tests verify the minimum qualification boundary for the
investigation/research foundation before Phase 12 is declared ready
for the next engineering phase.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.investigation.models import (
    Investigation,
    ResearchStatus,
)
from app.investigation.repository import InvestigationRepository
from app.investigation.service import InvestigationService
from database.migrations import migrate_investigation_schema


class Phase12QualificationTests(unittest.TestCase):
    """Validate the Phase 12 qualification boundary."""

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
                "CASE-QUALIFICATION",
                "Qualification Case",
                "IDEA",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
                "",
            ),
        )
        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()

    def test_investigation_memory_is_persistent_within_database(
        self,
    ) -> None:
        service = InvestigationService(
            self.connection
        )

        started_at = datetime(
            2026,
            1,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        )

        created = service.create(
            investigation_id="INV-QUALIFIED",
            case_id="CASE-QUALIFICATION",
            started_at=started_at,
        )

        self.assertEqual(
            created.status,
            ResearchStatus.NOT_STARTED,
        )

        repository = InvestigationRepository(
            self.connection
        )

        retrieved = repository.get(
            "INV-QUALIFIED"
        )

        self.assertIsNotNone(retrieved)
        self.assertEqual(
            retrieved.investigation_id,
            "INV-QUALIFIED",
        )
        self.assertEqual(
            retrieved.case_id,
            "CASE-QUALIFICATION",
        )

    def test_research_cannot_skip_required_review_stage(
        self,
    ) -> None:
        service = InvestigationService(
            self.connection
        )

        service.create(
            investigation_id="INV-REVIEW-GATE",
            case_id="CASE-QUALIFICATION",
            started_at=datetime.now(timezone.utc),
        )

        service.change_status(
            "INV-REVIEW-GATE",
            ResearchStatus.RESEARCHING,
        )

        with self.assertRaises(Exception):
            service.change_status(
                "INV-REVIEW-GATE",
                ResearchStatus.VERIFIED,
            )

    def test_verified_investigation_has_completion_timestamp(
        self,
    ) -> None:
        service = InvestigationService(
            self.connection
        )

        service.create(
            investigation_id="INV-COMPLETION",
            case_id="CASE-QUALIFICATION",
            started_at=datetime.now(timezone.utc),
        )

        service.change_status(
            "INV-COMPLETION",
            ResearchStatus.RESEARCHING,
        )

        service.change_status(
            "INV-COMPLETION",
            ResearchStatus.EVIDENCE_REVIEW,
        )

        verified = service.change_status(
            "INV-COMPLETION",
            ResearchStatus.VERIFIED,
        )

        self.assertEqual(
            verified.status,
            ResearchStatus.VERIFIED,
        )
        self.assertIsNotNone(
            verified.completed_at
        )
        self.assertGreaterEqual(
            verified.completed_at,
            verified.started_at,
        )

    def test_verified_state_is_terminal(self) -> None:
        service = InvestigationService(
            self.connection
        )

        service.create(
            investigation_id="INV-TERMINAL",
            case_id="CASE-QUALIFICATION",
            started_at=datetime.now(timezone.utc),
        )

        service.change_status(
            "INV-TERMINAL",
            ResearchStatus.RESEARCHING,
        )

        service.change_status(
            "INV-TERMINAL",
            ResearchStatus.EVIDENCE_REVIEW,
        )

        service.change_status(
            "INV-TERMINAL",
            ResearchStatus.VERIFIED,
        )

        with self.assertRaises(Exception):
            service.change_status(
                "INV-TERMINAL",
                ResearchStatus.RESEARCHING,
            )

    def test_phase12_does_not_create_a_second_case_database(
        self,
    ) -> None:
        tables = self.connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

        table_names = {
            row["name"]
            for row in tables
        }

        self.assertIn(
            "cases",
            table_names,
        )

        self.assertIn(
            "investigations",
            table_names,
        )

        self.assertNotIn(
            "investigation_cases",
            table_names,
        )


if __name__ == "__main__":
    unittest.main()
