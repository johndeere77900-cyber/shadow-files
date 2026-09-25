"""
Shadow Files Phase 12 qualification tests.

These tests provide the final qualification gate for the investigation
and research-memory foundation before downstream production phases begin.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.investigation.models import (
    ResearchStatus,
)
from app.investigation.service import InvestigationService
from database.investigation_schema import (
    create_investigation_schema,
)
from database.migrations import (
    migrate_investigation_schema,
)
from database.schema import create_schema


class Phase12QualificationTests(unittest.TestCase):
    """Final qualification tests for the Phase 12 foundation."""

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
                "CASE-QUALIFICATION",
                "Phase 12 Qualification Case",
                "IDEA",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
            ),
        )
        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()

    def test_investigation_schema_can_be_created_and_migrated(
        self,
    ) -> None:
        migrate_investigation_schema(self.connection)
        migrate_investigation_schema(self.connection)

        for table_name in (
            "investigations",
            "research_sources",
            "research_items",
            "investigation_timeline",
        ):
            row = self.connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = ?
                """,
                (table_name,),
            ).fetchone()

            self.assertEqual(
                row["count"],
                1,
                msg=f"Required table missing or duplicated: {table_name}",
            )

    def test_verified_investigation_has_completion_timestamp(
        self,
    ) -> None:
        service = InvestigationService(
            self.connection
        )

        service.create(
            investigation_id="INV-QUALIFIED",
            case_id="CASE-QUALIFICATION",
            started_at=datetime.now(timezone.utc),
        )

        service.change_status(
            "INV-QUALIFIED",
            ResearchStatus.RESEARCHING,
        )

        service.change_status(
            "INV-QUALIFIED",
            ResearchStatus.EVIDENCE_REVIEW,
        )

        investigation = service.change_status(
            "INV-QUALIFIED",
            ResearchStatus.VERIFIED,
        )

        self.assertEqual(
            investigation.status,
            ResearchStatus.VERIFIED,
        )
        self.assertIsNotNone(
            investigation.completed_at,
        )

    def test_incomplete_research_cannot_be_marked_verified(
        self,
    ) -> None:
        service = InvestigationService(
            self.connection
        )

        service.create(
            investigation_id="INV-INCOMPLETE-QUAL",
            case_id="CASE-QUALIFICATION",
            started_at=datetime.now(timezone.utc),
        )

        service.change_status(
            "INV-INCOMPLETE-QUAL",
            ResearchStatus.RESEARCHING,
        )

        service.change_status(
            "INV-INCOMPLETE-QUAL",
            ResearchStatus.INCOMPLETE,
        )

        with self.assertRaises(Exception):
            service.change_status(
                "INV-INCOMPLETE-QUAL",
                ResearchStatus.VERIFIED,
            )

    def test_existing_case_is_preserved(self) -> None:
        migrate_investigation_schema(self.connection)

        row = self.connection.execute(
            """
            SELECT
                case_id,
                title,
                state
            FROM cases
            WHERE case_id = ?
            """,
            ("CASE-QUALIFICATION",),
        ).fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(
            row["case_id"],
            "CASE-QUALIFICATION",
        )
        self.assertEqual(
            row["title"],
            "Phase 12 Qualification Case",
        )
        self.assertEqual(
            row["state"],
            "IDEA",
        )

    def test_phase12_tables_are_foreign_key_protected(
        self,
    ) -> None:
        migrate_investigation_schema(self.connection)

        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
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
                    "INV-ORPHAN-QUAL",
                    "CASE-DOES-NOT-EXIST",
                    "NOT_STARTED",
                    "2026-01-01T00:00:00+00:00",
                    None,
                    "",
                ),
            )


if __name__ == "__main__":
    unittest.main()
