"""
Shadow Files Phase 12 cascade-integrity tests.

These tests verify that deleting a case removes its investigation
records and their dependent research records without leaving
orphaned investigation data.
"""

import sqlite3
import unittest

from database.investigation_schema import (
    create_investigation_schema,
)
from database.schema import create_schema


class InvestigationCascadeTests(unittest.TestCase):
    """Validate investigation foreign-key cascade behavior."""

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
                "CASE-CASCADE",
                "Cascade Test Case",
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
                "INV-CASCADE",
                "CASE-CASCADE",
                "RESEARCHING",
                "2026-01-02T00:00:00+00:00",
                None,
                "",
            ),
        )

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
                "SRC-CASCADE",
                "INV-CASCADE",
                "Cascade Source",
                "https://example.com/source",
                "Example Publisher",
                "2026-01-02T01:00:00+00:00",
            ),
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
                "ITEM-CASCADE",
                "INV-CASCADE",
                "FACT",
                "Cascade test statement.",
                "2026-01-02T02:00:00+00:00",
                "SRC-CASCADE",
                "",
            ),
        )

        self.connection.execute(
            """
            INSERT INTO investigation_timeline (
                event_id,
                investigation_id,
                event_date,
                description,
                source_id,
                certainty,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "EVENT-CASCADE",
                "INV-CASCADE",
                "2026-01-03T00:00:00+00:00",
                "Cascade test event.",
                "SRC-CASCADE",
                "KNOWN",
                "",
            ),
        )

        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()

    def test_case_deletion_cascades_to_investigation(self) -> None:
        self.connection.execute(
            """
            DELETE FROM cases
            WHERE case_id = ?
            """,
            ("CASE-CASCADE",),
        )
        self.connection.commit()

        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM investigations
            WHERE investigation_id = ?
            """,
            ("INV-CASCADE",),
        ).fetchone()

        self.assertEqual(row["count"], 0)

    def test_case_deletion_cascades_to_research_sources(self) -> None:
        self.connection.execute(
            """
            DELETE FROM cases
            WHERE case_id = ?
            """,
            ("CASE-CASCADE",),
        )
        self.connection.commit()

        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM research_sources
            WHERE source_id = ?
            """,
            ("SRC-CASCADE",),
        ).fetchone()

        self.assertEqual(row["count"], 0)

    def test_case_deletion_cascades_to_research_items(self) -> None:
        self.connection.execute(
            """
            DELETE FROM cases
            WHERE case_id = ?
            """,
            ("CASE-CASCADE",),
        )
        self.connection.commit()

        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM research_items
            WHERE item_id = ?
            """,
            ("ITEM-CASCADE",),
        ).fetchone()

        self.assertEqual(row["count"], 0)

    def test_case_deletion_cascades_to_timeline_events(self) -> None:
        self.connection.execute(
            """
            DELETE FROM cases
            WHERE case_id = ?
            """,
            ("CASE-CASCADE",),
        )
        self.connection.commit()

        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM investigation_timeline
            WHERE event_id = ?
            """,
            ("EVENT-CASCADE",),
        ).fetchone()

        self.assertEqual(row["count"], 0)

    def test_no_orphaned_investigation_records_remain(self) -> None:
        self.connection.execute(
            """
            DELETE FROM cases
            WHERE case_id = ?
            """,
            ("CASE-CASCADE",),
        )
        self.connection.commit()

        for table_name, column_name, record_id in (
            (
                "investigations",
                "investigation_id",
                "INV-CASCADE",
            ),
            (
                "research_sources",
                "source_id",
                "SRC-CASCADE",
            ),
            (
                "research_items",
                "item_id",
                "ITEM-CASCADE",
            ),
            (
                "investigation_timeline",
                "event_id",
                "EVENT-CASCADE",
            ),
        ):
            row = self.connection.execute(
                f"""
                SELECT COUNT(*) AS count
                FROM {table_name}
                WHERE {column_name} = ?
                """,
                (record_id,),
            ).fetchone()

            self.assertEqual(
                row["count"],
                0,
                msg=(
                    f"Orphaned record remained in "
                    f"{table_name}: {record_id}"
                ),
            )


if __name__ == "__main__":
    unittest.main()
