"""
Shadow Files Phase 12 investigation service tests.

These tests verify that the investigation service creates
investigations and enforces the research lifecycle without allowing
invalid transitions.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.investigation.models import ResearchStatus
from app.investigation.service import InvestigationService
from database.investigation_schema import create_investigation_schema
from database.migrations import migrate


class InvestigationServiceTests(unittest.TestCase):
    """Verify investigation service behavior."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

        migrate(self.connection)

        now = datetime.now(timezone.utc)

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
                "Service Test Case",
                "IDEA",
                now.isoformat(),
                now.isoformat(),
            ),
        )
        self.connection.commit()

        create_investigation_schema(self.connection)

        self.service = InvestigationService(
            self.connection
        )
        self.now = now

    def tearDown(self) -> None:
        self.connection.close()

    def test_create_starts_in_not_started_state(self) -> None:
        investigation = self.service.create(
            investigation_id="INV-001",
            case_id="CASE-001",
            started_at=self.now,
        )

        self.assertEqual(
            investigation.status,
            ResearchStatus.NOT_STARTED,
        )

        stored = self.service.get("INV-001")

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.status,
            ResearchStatus.NOT_STARTED,
        )

    def test_change_status_to_researching(self) -> None:
        self.service.create(
            investigation_id="INV-002",
            case_id="CASE-001",
            started_at=self.now,
        )

        updated = self.service.change_status(
            "INV-002",
            ResearchStatus.RESEARCHING,
        )

        self.assertEqual(
            updated.status,
            ResearchStatus.RESEARCHING,
        )

    def test_research_can_enter_evidence_review(self) -> None:
        self.service.create(
            investigation_id="INV-003",
            case_id="CASE-001",
            started_at=self.now,
        )

        self.service.change_status(
            "INV-003",
            ResearchStatus.RESEARCHING,
        )

        updated = self.service.change_status(
            "INV-003",
            ResearchStatus.EVIDENCE_REVIEW,
        )

        self.assertEqual(
            updated.status,
            ResearchStatus.EVIDENCE_REVIEW,
        )

    def test_evidence_review_can_be_verified(self) -> None:
        self.service.create(
            investigation_id="INV-004",
            case_id="CASE-001",
            started_at=self.now,
        )

        self.service.change_status(
            "INV-004",
            ResearchStatus.RESEARCHING,
        )

        self.service.change_status(
            "INV-004",
            ResearchStatus.EVIDENCE_REVIEW,
        )

        updated = self.service.change_status(
            "INV-004",
            ResearchStatus.VERIFIED,
        )

        self.assertEqual(
            updated.status,
            ResearchStatus.VERIFIED,
        )

        self.assertIsNotNone(
            updated.completed_at
        )

    def test_invalid_transition_is_rejected(self) -> None:
        self.service.create(
            investigation_id="INV-005",
            case_id="CASE-001",
            started_at=self.now,
        )

        with self.assertRaises(Exception):
            self.service.change_status(
                "INV-005",
                ResearchStatus.VERIFIED,
            )

    def test_missing_investigation_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            self.service.change_status(
                "UNKNOWN",
                ResearchStatus.RESEARCHING,
            )


if __name__ == "__main__":
    unittest.main()
