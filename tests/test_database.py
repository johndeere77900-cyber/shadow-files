"""
Shadow Files database tests.

Phase 7 database tests expanded for Phase 11.

These tests verify schema version 2, migration compatibility,
case persistence, evidence persistence, and the supporting
claim/source/link tables.
"""

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from database.connection import get_connection
from database.migrations import get_schema_version, migrate
from database.repository import DatabaseRepository
from database.schema import SCHEMA_VERSION, create_schema


class DatabaseTests(unittest.TestCase):
    """Verify the persistent database foundation."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def tearDown(self) -> None:
        self.connection.close()

    def test_schema_version_is_current(self) -> None:
        create_schema(self.connection)

        self.assertEqual(
            get_schema_version(self.connection),
            SCHEMA_VERSION,
        )
        self.assertEqual(SCHEMA_VERSION, 2)

    def test_schema_creation_is_idempotent(self) -> None:
        create_schema(self.connection)
        create_schema(self.connection)

        tables = {
            row["name"]
            for row in self.connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        self.assertIn("cases", tables)
        self.assertIn("jobs", tables)
        self.assertIn("audit_events", tables)
        self.assertIn("evidence", tables)
        self.assertIn("claims", tables)
        self.assertIn("evidence_sources", tables)
        self.assertIn("claim_evidence_links", tables)

    def test_migrate_new_database(self) -> None:
        version = migrate(self.connection)

        self.assertEqual(version, 2)
        self.assertEqual(
            get_schema_version(self.connection),
            2,
        )

    def test_migrate_existing_version_one_database(self) -> None:
        with self.connection:
            self.connection.executescript(
                """
                CREATE TABLE schema_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE cases (
                    case_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE jobs (
                    job_id TEXT PRIMARY KEY,
                    operation TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE audit_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    command TEXT NOT NULL,
                    target TEXT,
                    previous_state TEXT,
                    new_state TEXT,
                    result TEXT NOT NULL,
                    error TEXT,
                    provider TEXT,
                    job_id TEXT,
                    FOREIGN KEY (job_id)
                        REFERENCES jobs(job_id)
                        ON DELETE SET NULL
                );

                INSERT INTO schema_metadata (
                    key,
                    value
                )
                VALUES (
                    'schema_version',
                    '1'
                );
                """
            )

        version = migrate(self.connection)

        self.assertEqual(version, 2)
        self.assertEqual(
            get_schema_version(self.connection),
            2,
        )

        evidence_table = self.connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'evidence'
            """
        ).fetchone()

        self.assertIsNotNone(evidence_table)

    def test_database_repository_case_round_trip(self) -> None:
        create_schema(self.connection)
        repository = DatabaseRepository(self.connection)

        created_at = datetime.now(timezone.utc)

        repository.create_case(
            case_id="CASE-001",
            title="Test Case",
            state="IDEA",
            created_at=created_at,
            updated_at=created_at,
        )

        case = repository.get_case("CASE-001")

        self.assertIsNotNone(case)
        self.assertEqual(case.title, "Test Case")
        self.assertEqual(case.state, "IDEA")

    def test_database_can_create_evidence_record(self) -> None:
        create_schema(self.connection)

        created_at = datetime.now(timezone.utc).isoformat()

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
                "Test Case",
                "IDEA",
                created_at,
                created_at,
            ),
        )

        self.connection.execute(
            """
            INSERT INTO evidence (
                evidence_id,
                case_id,
                claim,
                source_name,
                source_url,
                evidence_type,
                status,
                retrieved_at,
                publication_date,
                reliability_assessment,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "EVIDENCE-001",
                "CASE-001",
                "A test factual claim.",
                "Test Source",
                "https://example.com",
                "CREDIBLE_REPORT",
                "REVIEWED",
                created_at,
                None,
                "Test assessment",
                "",
            ),
        )

        self.connection.commit()

        row = self.connection.execute(
            """
            SELECT evidence_id, case_id, claim
            FROM evidence
            WHERE evidence_id = ?
            """,
            ("EVIDENCE-001",),
        ).fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(
            row["case_id"],
            "CASE-001",
        )
        self.assertEqual(
            row["claim"],
            "A test factual claim.",
        )

    def test_phase11_support_tables_have_foreign_keys(self) -> None:
        create_schema(self.connection)

        claims_fk = self.connection.execute(
            """
            PRAGMA foreign_key_list(claims)
            """
        ).fetchall()

        links_fk = self.connection.execute(
            """
            PRAGMA foreign_key_list(claim_evidence_links)
            """
        ).fetchall()

        claim_targets = {
            row["table"]
            for row in claims_fk
        }

        link_targets = {
            row["table"]
            for row in links_fk
        }

        self.assertIn("cases", claim_targets)
        self.assertIn(
            "claims",
            link_targets,
        )
        self.assertIn(
            "evidence",
            link_targets,
        )

    def test_foreign_key_prevents_evidence_for_unknown_case(
        self,
    ) -> None:
        create_schema(self.connection)

        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                """
                INSERT INTO evidence (
                    evidence_id,
                    case_id,
                    claim,
                    source_name,
                    source_url,
                    evidence_type,
                    status,
                    retrieved_at,
                    publication_date,
                    reliability_assessment,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "EVIDENCE-INVALID",
                    "UNKNOWN-CASE",
                    "Invalid claim",
                    "Test Source",
                    None,
                    "OTHER",
                    "UNREVIEWED",
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
                    None,
                    "",
                    "",
                ),
            )

    def test_file_database_can_be_initialized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = (
                Path(directory) / "shadow_files.db"
            )

            connection = get_connection(database_path)

            try:
                version = migrate(connection)

                self.assertEqual(version, 2)
                self.assertTrue(
                    database_path.exists()
                )
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
