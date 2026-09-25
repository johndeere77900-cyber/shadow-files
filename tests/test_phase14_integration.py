"""
Phase 14 scheduler integration tests.
"""

import sqlite3
import unittest
from datetime import datetime, timedelta, timezone

from app.scheduler.constraints import validate_schedule_set
from app.scheduler.deadlines import build_standard_deadlines
from app.scheduler.models import ScheduleStatus, ScheduleType
from app.scheduler.planner import build_schedule_pair
from app.scheduler.repository import ScheduleRepository
from app.scheduler.service import SchedulerService
from app.scheduler.weekly_plan import (
    WeeklyPublicationRule,
    build_monthly_publication_plan,
)
from database.production_schema import create_production_schema
from database.scheduler_schema import create_scheduler_schema


UTC = timezone.utc


class Phase14IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("PRAGMA foreign_keys = ON")

        self.connection.executescript(
            """
            CREATE TABLE cases (
                case_id TEXT PRIMARY KEY,
                title TEXT NOT NULL
            );
            """
        )

        create_production_schema(
            self.connection
        )

        create_scheduler_schema(
            self.connection
        )

        self.connection.execute(
            """
            INSERT INTO cases (
                case_id,
                title
            )
            VALUES (?, ?)
            """,
            (
                "case-001",
                "Test Case",
            ),
        )

        self.connection.execute(
            """
            INSERT INTO productions (
                production_id,
                case_id,
                title,
                content_type,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "prod-001",
                "case-001",
                "Shadow Files Test Episode",
                "STORY",
                "NOT_STARTED",
                "2026-10-01T10:00:00+00:00",
                "2026-10-01T10:00:00+00:00",
            ),
        )

        self.connection.commit()

        self.repository = ScheduleRepository(
            self.connection
        )

        self.service = SchedulerService(
            self.repository
        )

    def tearDown(self):
        self.connection.close()

    def test_full_scheduler_planning_flow(self):
        production_time = datetime(
            2026,
            10,
            6,
            18,
            0,
            tzinfo=UTC,
        )

        publication_time = datetime(
            2026,
            10,
            6,
            20,
            0,
            tzinfo=UTC,
        )

        slots = build_schedule_pair(
            production_id="prod-001",
            production_time=production_time,
            publication_time=publication_time,
            timezone_name="UTC",
            preparation_hours=24,
        )

        validate_schedule_set(slots)

        for slot in slots:
            self.repository.create(slot)

        stored = self.repository.list_for_production(
            "prod-001"
        )

        self.assertEqual(
            len(stored),
            2,
        )

        self.assertEqual(
            stored[0].schedule_type,
            ScheduleType.PRODUCTION,
        )

        self.assertEqual(
            stored[1].schedule_type,
            ScheduleType.PUBLICATION,
        )

    def test_scheduler_lifecycle_flow(self):
        scheduled_for = datetime(
            2026,
            10,
            6,
            20,
            0,
            tzinfo=UTC,
        )

        self.service.create_schedule(
            schedule_id="publication-001",
            production_id="prod-001",
            schedule_type=ScheduleType.PUBLICATION,
            scheduled_for=scheduled_for,
        )

        active = self.service.activate(
            "publication-001"
        )

        self.assertEqual(
            active.status,
            ScheduleStatus.ACTIVE,
        )

        completed = self.service.complete(
            "publication-001"
        )

        self.assertEqual(
            completed.status,
            ScheduleStatus.COMPLETED,
        )

    def test_scheduler_deadlines_integrate_with_publication_plan(self):
        publication_time = datetime(
            2026,
            10,
            6,
            20,
            0,
            tzinfo=UTC,
        )

        deadlines = build_standard_deadlines(
            production_id="prod-001",
            publication_time=publication_time,
        )

        self.assertEqual(
            len(deadlines),
            4,
        )

        self.assertLess(
            deadlines[-1].due_at,
            publication_time,
        )

    def test_weekly_publication_plan_produces_four_slots(self):
        start = datetime(
            2026,
            10,
            1,
            10,
            0,
            tzinfo=UTC,
        )

        rule = WeeklyPublicationRule(
            weekday=1,
            hour=20,
            minute=0,
            timezone_name="UTC",
            occurrences=4,
        )

        publication_slots = build_monthly_publication_plan(
            start,
            rule,
        )

        self.assertEqual(
            len(publication_slots),
            4,
        )

        for index in range(1, 4):
            self.assertEqual(
                publication_slots[index]
                - publication_slots[index - 1],
                timedelta(weeks=1),
            )

    def test_due_schedule_can_be_found_and_completed(self):
        scheduled_for = datetime(
            2026,
            10,
            6,
            20,
            0,
            tzinfo=UTC,
        )

        self.service.create_schedule(
            schedule_id="publication-001",
            production_id="prod-001",
            schedule_type=ScheduleType.PUBLICATION,
            scheduled_for=scheduled_for,
        )

        due = self.service.list_due(
            scheduled_for + timedelta(minutes=1)
        )

        self.assertEqual(
            len(due),
            1,
        )

        self.service.activate(
            "publication-001"
        )

        completed = self.service.complete(
            "publication-001"
        )

        self.assertEqual(
            completed.status,
            ScheduleStatus.COMPLETED,
        )

    def test_foreign_key_requires_existing_production(self):
        scheduled_for = datetime(
            2026,
            10,
            6,
            20,
            0,
            tzinfo=UTC,
        )

        with self.assertRaises(
            sqlite3.IntegrityError
        ):
            self.service.create_schedule(
                schedule_id="publication-001",
                production_id="missing-production",
                schedule_type=ScheduleType.PUBLICATION,
                scheduled_for=scheduled_for,
            )

    def test_scheduler_schema_is_idempotent(self):
        create_scheduler_schema(
            self.connection
        )

        create_scheduler_schema(
            self.connection
        )

        table = self.connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'schedule_slots'
            """
        ).fetchone()

        self.assertIsNotNone(table)


if __name__ == "__main__":
    unittest.main()
