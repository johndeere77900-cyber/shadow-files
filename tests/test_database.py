"""
Shadow Files database tests.

Phase 7 tests the persistent database foundation, including:

- schema creation
- schema version tracking
- migrations
- case persistence
- job persistence
- audit-event persistence
- foreign-key behavior
"""

import sqlite3
import unittest

from database.migrations import get_schema_version, migrate
from database.models import (
    AuditEventRecord,
    CaseRecord,
    JobRecord,
)
from database.repository import DatabaseRepository
from database.schema import SCHEMA_VERSION


class DatabaseTestCase(unittest.TestCase):
    """Shared in-memory database setup for Phase 7 tests."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

        migrate(self.connection)

        self.repository = DatabaseRepository(
            self.connection
        )

    def tearDown(self) -> None:
        self.connection.close()


class TestDatabaseSchema(DatabaseTestCase):
    """Test database schema and migration behavior."""

    def test_schema_version_is_current(self) -> None:
        self.assertEqual(
            get_schema_version(self.connection),
            SCHEMA_VERSION,
        )

    def test_required_tables_exist(self) -> None:
        rows = self.connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

        table_names = {
            row["name"]
            for row in rows
        }

        self.assertIn(
            "schema_metadata",
            table_names,
        )
        self.assertIn(
            "cases",
            table_names,
        )
        self.assertIn(
            "jobs",
            table_names,
        )
        self.assertIn(
            "audit_events",
            table_names,
        )

    def test_migration_is_idempotent(self) -> None:
        first_version = migrate(
            self.connection
        )

        second_version = migrate(
            self.connection
        )

        self.assertEqual(
            first_version,
            SCHEMA_VERSION,
        )
        self.assertEqual(
            second_version,
            SCHEMA_VERSION,
        )


class TestCaseRepository(DatabaseTestCase):
    """Test persistent case records."""

    def test_create_and_get_case(self) -> None:
        case = CaseRecord(
            case_id="CASE-001",
            title="Test Case",
            state="IDEA",
            created_at="2026-09-24T10:00:00+00:00",
            updated_at="2026-09-24T10:00:00+00:00",
        )

        self.repository.create_case(case)

        stored = self.repository.get_case(
            "CASE-001"
        )

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.case_id,
            case.case_id,
        )
        self.assertEqual(
            stored.title,
            case.title,
        )
        self.assertEqual(
            stored.state,
            "IDEA",
        )

    def test_update_case_state(self) -> None:
        case = CaseRecord(
            case_id="CASE-002",
            title="State Test",
            state="IDEA",
            created_at="2026-09-24T10:00:00+00:00",
            updated_at="2026-09-24T10:00:00+00:00",
        )

        self.repository.create_case(case)

        self.repository.update_case_state(
            case_id="CASE-002",
            state="CASE_SELECTED",
            updated_at="2026-09-24T10:05:00+00:00",
        )

        stored = self.repository.get_case(
            "CASE-002"
        )

        self.assertEqual(
            stored.state,
            "CASE_SELECTED",
        )
        self.assertEqual(
            stored.updated_at,
            "2026-09-24T10:05:00+00:00",
        )

    def test_missing_case_update_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            self.repository.update_case_state(
                case_id="DOES-NOT-EXIST",
                state="RESEARCHING",
                updated_at="2026-09-24T10:00:00+00:00",
            )


class TestJobRepository(DatabaseTestCase):
    """Test persistent job records."""

    def test_create_and_get_job(self) -> None:
        job = JobRecord(
            job_id="JOB-001",
            operation="research_case",
            status="PENDING",
            created_at="2026-09-24T10:00:00+00:00",
        )

        self.repository.create_job(job)

        stored = self.repository.get_job(
            "JOB-001"
        )

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.job_id,
            "JOB-001",
        )
        self.assertEqual(
            stored.operation,
            "research_case",
        )
        self.assertEqual(
            stored.status,
            "PENDING",
        )

    def test_update_job_status(self) -> None:
        job = JobRecord(
            job_id="JOB-002",
            operation="generate_script",
            status="PENDING",
            created_at="2026-09-24T10:00:00+00:00",
        )

        self.repository.create_job(job)

        self.repository.update_job_status(
            job_id="JOB-002",
            status="RUNNING",
        )

        stored = self.repository.get_job(
            "JOB-002"
        )

        self.assertEqual(
            stored.status,
            "RUNNING",
        )

    def test_missing_job_update_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            self.repository.update_job_status(
                job_id="DOES-NOT-EXIST",
                status="FAILED",
            )


class TestAuditRepository(DatabaseTestCase):
    """Test persistent audit-event records."""

    def test_create_and_get_audit_event(self) -> None:
        job = JobRecord(
            job_id="JOB-AUDIT-001",
            operation="test_operation",
            status="PENDING",
            created_at="2026-09-24T10:00:00+00:00",
        )

        self.repository.create_job(job)

        event = AuditEventRecord(
            event_id="EVENT-001",
            timestamp="2026-09-24T10:01:00+00:00",
            actor="system",
            intent="test",
            command="test command",
            target="CASE-001",
            previous_state="IDEA",
            new_state="CASE_SELECTED",
            result="success",
            job_id="JOB-AUDIT-001",
        )

        self.repository.create_audit_event(event)

        stored = self.repository.get_audit_event(
            "EVENT-001"
        )

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.event_id,
            "EVENT-001",
        )
        self.assertEqual(
            stored.result,
            "success",
        )
        self.assertEqual(
            stored.job_id,
            "JOB-AUDIT-001",
        )

    def test_audit_events_can_be_filtered_by_job(self) -> None:
        job = JobRecord(
            job_id="JOB-AUDIT-002",
            operation="audit_test",
            status="PENDING",
            created_at="2026-09-24T10:00:00+00:00",
        )

        self.repository.create_job(job)

        event_one = AuditEventRecord(
            event_id="EVENT-002",
            timestamp="2026-09-24T10:01:00+00:00",
            actor="system",
            intent="test",
            command="command one",
            target="CASE-001",
            previous_state=None,
            new_state=None,
            result="success",
            job_id="JOB-AUDIT-002",
        )

        event_two = AuditEventRecord(
            event_id="EVENT-003",
            timestamp="2026-09-24T10:02:00+00:00",
            actor="system",
            intent="test",
            command="command two",
            target="CASE-002",
            previous_state=None,
            new_state=None,
            result="success",
            job_id=None,
        )

        self.repository.create_audit_event(
            event_one
        )
        self.repository.create_audit_event(
            event_two
        )

        filtered = self.repository.list_audit_events(
            job_id="JOB-AUDIT-002"
        )

        self.assertEqual(
            len(filtered),
            1,
        )
        self.assertEqual(
            filtered[0].event_id,
            "EVENT-002",
        )

    def test_deleting_job_preserves_audit_event(self) -> None:
        job = JobRecord(
            job_id="JOB-AUDIT-003",
            operation="delete_test",
            status="PENDING",
            created_at="2026-09-24T10:00:00+00:00",
        )

        self.repository.create_job(job)

        event = AuditEventRecord(
            event_id="EVENT-004",
            timestamp="2026-09-24T10:03:00+00:00",
            actor="system",
            intent="test",
            command="delete job",
            target="JOB-AUDIT-003",
            previous_state=None,
            new_state=None,
            result="success",
            job_id="JOB-AUDIT-003",
        )

        self.repository.create_audit_event(event)

        self.connection.execute(
            """
            DELETE FROM jobs
            WHERE job_id = ?
            """,
            ("JOB-AUDIT-003",),
        )
        self.connection.commit()

        stored = self.repository.get_audit_event(
            "EVENT-004"
        )

        self.assertIsNotNone(stored)
        self.assertIsNone(
            stored.job_id
        )


if __name__ == "__main__":
    unittest.main()
