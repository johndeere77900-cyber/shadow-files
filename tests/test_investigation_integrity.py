"""
Shadow Files Phase 12 investigation-integrity tests.

These tests verify that research records remain separated from
verified case evidence and that incomplete research cannot be
mistaken for verified research.
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
from app.investigation.service import InvestigationService
from database.investigation_schema import (
    create_investigation_schema,
)
from database.schema import create_schema


class InvestigationIntegrityTests(unittest.TestCase):
    """Validate separation and integrity of research state."""

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
                updated_at,
                summary
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "CASE-INTEGRITY",
                "Integrity Test Case",
                "IDEA",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
                "",
            ),
        )
        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()

    def test_new_investigation_is_not_verified(self) -> None:
        investigation = Investigation(
            investigation_id="INV-INTEGRITY",
            case_id="CASE-INTEGRITY",
            status=ResearchStatus.NOT_STARTED,
            started_at=datetime.now(timezone.utc),
        )

        self.assertNotEqual(
            investigation.status,
            ResearchStatus.VERIFIED,
        )

    def test_research_item_does_not_create_case_evidence(
        self,
    ) -> None:
        service = InvestigationService(self.connection)

        service.create(
            investigation_id="INV-EVIDENCE-SEPARATION",
            case_id="CASE-INTEGRITY",
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
                "ITEM-SEPARATION",
                "INV-EVIDENCE-SEPARATION",
                ResearchItemType.FACT.value,
                "Research discovery only.",
                "2026-01-01T02:00:00+00:00",
                None,
                "",
            ),
        )
        self.connection.commit()

        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM evidence
            WHERE case_id = ?
            """,
            ("CASE-INTEGRITY",),
        ).fetchone()

        self.assertEqual(row["count"], 0)

    def test_incomplete_investigation_cannot_transition_directly_to_verified(
        self,
    ) -> None:
        service = InvestigationService(self.connection)

        service.create(
            investigation_id="INV-INCOMPLETE",
            case_id="CASE-INTEGRITY",
            started_at=datetime.now(timezone.utc),
        )

        service.change_status(
            "INV-INCOMPLETE",
            ResearchStatus.RESEARCHING,
        )

        service.change_status(
            "INV-INCOMPLETE",
            ResearchStatus.INCOMPLETE,
        )

        with self.assertRaises(Exception):
            service.change_status(
                "INV-INCOMPLETE",
                ResearchStatus.VERIFIED,
            )

    def test_verified_status_requires_evidence_review_path(
        self,
    ) -> None:
        service = InvestigationService(self.connection)

        service.create(
            investigation_id="INV-VERIFICATION-PATH",
            case_id="CASE-INTEGRITY",
            started_at=datetime.now(timezone.utc),
        )

        service.change_status(
            "INV-VERIFICATION-PATH",
            ResearchStatus.RESEARCHING,
        )

        service.change_status(
            "INV-VERIFICATION-PATH",
            ResearchStatus.EVIDENCE_REVIEW,
        )

        verified = service.change_status(
            "INV-VERIFICATION-PATH",
            ResearchStatus.VERIFIED,
        )

        self.assertEqual(
            verified.status,
            ResearchStatus.VERIFIED,
        )

        self.assertIsNotNone(
            verified.completed_at,
        )

    def test_verified_investigation_cannot_be_reopened(self) -> None:
        service = InvestigationService(self.connection)

        service.create(
            investigation_id="INV-IMMUTABLE-STATUS",
            case_id="CASE-INTEGRITY",
            started_at=datetime.now(timezone.utc),
        )

        service.change_status(
            "INV-IMMUTABLE-STATUS",
            ResearchStatus.RESEARCHING,
        )

        service.change_status(
            "INV-IMMUTABLE-STATUS",
            ResearchStatus.EVIDENCE_REVIEW,
        )

        service.change_status(
            "INV-IMMUTABLE-STATUS",
            ResearchStatus.VERIFIED,
        )

        with self.assertRaises(Exception):
            service.change_status(
                "INV-IMMUTABLE-STATUS",
                ResearchStatus.RESEARCHING,
            )


if __name__ == "__main__":
    unittest.main()
