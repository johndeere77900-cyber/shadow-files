"""
Shadow Files Phase 12 migration-preservation tests.

These tests verify that adding the investigation schema does not
destroy or alter existing case, evidence, or audit data.
"""

import sqlite3
import unittest

from database.migrations import migrate_investigation_schema
from database.schema import create_schema


class InvestigationMigrationTests(unittest.TestCase):
    """Validate safe migration into the Phase 12 schema."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")

        create_schema(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def test_existing_case_survives_investigation_migration(self) -> None:
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
                "CASE-001",
                "Existing Case",
                "IDEA",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
                "Existing case record.",
            ),
        )
        self.connection.commit()

        migrate_investigation_schema(self.connection)

        row = self.connection.execute(
            """
            SELECT
                case_id,
                title,
                state,
                summary
            FROM cases
            WHERE case_id = ?
            """,
            ("CASE-001",),
        ).fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["case_id"], "CASE-001")
        self.assertEqual(row["title"], "Existing Case")
        self.assertEqual(row["state"], "IDEA")
        self.assertEqual(
            row["summary"],
            "Existing case record.",
        )

    def test_existing_audit_table_survives_migration(self) -> None:
        migrate_investigation_schema(self.connection)

        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'audit_events'
            """
        ).fetchone()

        self.assertEqual(row["count"], 1)

    def test_investigation_records_can_reference_existing_cases(
        self,
    ) -> None:
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
                "CASE-002",
                "Migration Test Case",
                "IDEA",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
                "",
            ),
        )
        self.connection.commit()

        migrate_investigation_schema(self.connection)

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
                "INV-002",
                "CASE-002",
                "NOT_STARTED",
                "2026-01-02T00:00:00+00:00",
                None,
                "",
            ),
        )
        self.connection.commit()

        row = self.connection.execute(
            """
            SELECT
                investigation_id,
                case_id,
                status
            FROM investigations
            WHERE investigation_id = ?
            """,
            ("INV-002",),
        ).fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["case_id"], "CASE-002")
        self.assertEqual(
            row["status"],
            "NOT_STARTED",
        )

    def test_migration_does_not_duplicate_investigation_tables(
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
                msg=f"Duplicate table detected: {table_name}",
            )


if __name__ == "__main__":
    unittest.main()
