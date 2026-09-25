"""
Shadow Files Phase 12 investigation-schema tests.

These tests verify that the investigation schema can be created
independently and repeatedly without damaging the existing core schema.
"""

import sqlite3
import unittest

from database.investigation_schema import (
    create_investigation_schema,
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

    def test_investigation_schema_creates_required_tables(self) -> None:
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

    def test_investigation_schema_is_idempotent(self) -> None:
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

            self.assertEqual(
                row["count"],
                1,
                msg=f"Unexpected duplicate table: {table_name}",
            )

    def test_investigations_require_existing_case(self) -> None:
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
                    "INV-ORPHAN",
                    "CASE-MISSING",
                    "NOT_STARTED",
                    "2026-01-01T00:00:00+00:00",
                    None,
                    "",
                ),
            )

    def test_research_source_requires_investigation_when_defined(
        self,
    ) -> None:
        create_investigation_schema(self.connection)

        columns = self.connection.execute(
            """
            PRAGMA table_info(research_sources)
            """
        ).fetchall()

        column_names = {
            row["name"]
            for row in columns
        }

        self.assertIn(
            "source_id",
            column_names,
        )
        self.assertIn(
            "investigation_id",
            column_names,
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
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "CASE-SCHEMA",
                "Schema Test Case",
                "IDEA",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
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
                "INV-SCHEMA",
                "CASE-SCHEMA",
                "NOT_STARTED",
                "2026-01-01T00:00:00+00:00",
                None,
                "",
            ),
        )
        self.connection.commit()

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
                    "ITEM-ORPHAN-SOURCE",
                    "INV-SCHEMA",
                    "FACT",
                    "Research statement.",
                    "2026-01-01T01:00:00+00:00",
                    "SOURCE-MISSING",
                    "",
                ),
            )

    def test_core_case_schema_remains_unchanged(self) -> None:
        create_investigation_schema(self.connection)

        columns = self.connection.execute(
            """
            PRAGMA table_info(cases)
            """
        ).fetchall()

        column_names = [
            row["name"]
            for row in columns
        ]

        self.assertEqual(
            column_names,
            [
                "case_id",
                "title",
                "state",
                "created_at",
                "updated_at",
            ],
        )


if __name__ == "__main__":
    unittest.main()
