"""
Shadow Files Phase 12 investigation-schema tests.

These tests verify that the investigation schema can be created,
re-created safely, and maintains the required foreign-key relationships.
"""

import sqlite3
import unittest

from database.investigation_schema import (
    create_investigation_schema,
)
from database.migrations import (
    migrate_investigation_schema,
)
from database.schema import create_schema


class InvestigationSchemaTests(unittest.TestCase):
    """Validate the Phase 12 investigation database schema."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")

        create_schema(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def test_investigation_tables_are_created(self) -> None:
        create_investigation_schema(self.connection)

        expected_tables = {
            "investigations",
            "research_sources",
            "research_items",
            "investigation_timeline",
        }

        rows = self.connection.execute(
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
            expected_tables.issubset(actual_tables)
        )

    def test_schema_creation_is_idempotent(self) -> None:
        create_investigation_schema(self.connection)
        create_investigation_schema(self.connection)

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

            self.assertEqual(row["count"], 1)

    def test_investigation_requires_existing_case(self) -> None:
        create_investigation_schema(self.connection)

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
                    "INV-001",
                    "CASE-MISSING",
                    "NOT_STARTED",
                    "2026-01-01T00:00:00+00:00",
                    None,
                    "",
                ),
            )

    def test_child_records_require_existing_investigation(self) -> None:
        create_investigation_schema(self.connection)

        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
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
                    "SRC-001",
                    "INV-MISSING",
                    "Example Source",
                    None,
                    None,
                    "2026-01-01T00:00:00+00:00",
                ),
            )

    def test_research_item_source_must_exist_when_provided(
        self,
    ) -> None:
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
                "CASE-001",
                "Test Case",
                "IDEA",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
                "",
            ),
        )

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
                "INV-001",
                "CASE-001",
                "RESEARCHING",
                "2026-01-01T00:00:00+00:00",
                None,
                "",
            ),
        )

        with self.assertRaises(sqlite3.IntegrityError):
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
                    "ITEM-001",
                    "INV-001",
                    "FACT",
                    "Test statement",
                    "2026-01-01T00:00:00+00:00",
                    "SRC-MISSING",
                    "",
                ),
            )

    def test_investigation_migration_creates_required_tables(
        self,
    ) -> None:
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")

        try:
            migrate_investigation_schema(connection)

            expected_tables = {
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
                expected_tables.issubset(actual_tables)
            )
        finally:
            connection.close()

    def test_investigation_migration_is_idempotent(self) -> None:
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")

        try:
            migrate_investigation_schema(connection)
            migrate_investigation_schema(connection)

            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = 'investigations'
                """
            ).fetchone()

            self.assertEqual(row["count"], 1)
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
