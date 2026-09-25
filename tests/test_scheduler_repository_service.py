"""
Tests for Shadow Files scheduler repository and service.
"""

import sqlite3
import unittest
from datetime import datetime, timedelta, timezone

from app.scheduler.events import (
    ScheduleEvent,
    ScheduleEventRepository,
)
from app.scheduler.models import (
    ScheduleStatus,
    ScheduleType,
)
from app.scheduler.repository import ScheduleRepository
from app.scheduler.service import SchedulerService
from database.production_schema import create_production_schema
from database.scheduler_schema import create_scheduler_schema


UTC = timezone.utc


class SchedulerRepositoryServiceTests(unittest.TestCase):

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("PRAGMA foreign_keys = ON")

        create_production_schema(
            self.connection
        )
        create_scheduler_schema(
            self.connection
        )

        self._create_production()

        self.repository = ScheduleRepository(
            self.connection
        )

        self.service = SchedulerService(
            self.repository
        )

    def tearDown(self):
        self.connection.close()

    def _create_production(self):
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
                "Test Production",
                "STORY",
                "NOT_STARTED",
                "2026-10-01T10:00:00+00:00",
                "2026-10-01T10:00:00+00:00",
            ),
        )

        self.connection.commit()

    def _scheduled_time(self):
        return datetime(
            2026,
            10,
            6,
            20,
            0,
            tzinfo=UTC,
        )

    def test_create_and_get_schedule(self):
        slot = self.service.create_schedule(
            schedule_id="schedule-001",
            production_id="prod-001",
            schedule_type=ScheduleType.PUBLICATION,
            scheduled_for=self._scheduled_time(),
            deadline=self._scheduled_time()
            - timedelta(hours=24),
            timezone_name="UTC",
        )

        self.assertEqual(
            slot.status,
            ScheduleStatus.PLANNED,
        )

        stored = self.service.get_schedule(
            "schedule-001"
        )

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.schedule_id,
            "schedule-001",
        )

    def test_schedule_can_be_activated(self):
        self.service.create_schedule(
            "schedule-001",
            "prod-001",
            ScheduleType.PUBLICATION,
            self._scheduled_time(),
        )

        updated = self.service.activate(
            "schedule-001"
        )

        self.assertEqual(
            updated.status,
            ScheduleStatus.ACTIVE,
        )

    def test_active_schedule_can_be_completed(self):
        self.service.create_schedule(
            "schedule-001",
            "prod-001",
            ScheduleType.PUBLICATION,
            self._scheduled_time(),
        )

        self.service.activate(
            "schedule-001"
        )

        updated = self.service.complete(
            "schedule-001"
        )

        self.assertEqual(
            updated.status,
            ScheduleStatus.COMPLETED,
        )

    def test_invalid_transition_is_rejected(self):
        self.service.create_schedule(
            "schedule-001",
            "prod-001",
            ScheduleType.PUBLICATION,
            self._scheduled_time(),
        )

        with self.assertRaises(ValueError):
            self.service.complete(
                "schedule-001"
            )

    def test_missing_schedule_is_rejected(self):
        with self.assertRaises(KeyError):
            self.service.activate(
                "missing-schedule"
            )

    def test_list_for_production(self):
        self.service.create_schedule(
            "schedule-001",
            "prod-001",
            ScheduleType.PRODUCTION,
            self._scheduled_time()
            - timedelta(hours=2),
        )

        self.service.create_schedule(
            "schedule-002",
            "prod-001",
            ScheduleType.PUBLICATION,
            self._scheduled_time(),
        )

        schedules = self.repository.list_for_production(
            "prod-001"
        )

        self.assertEqual(
            len(schedules),
            2,
        )

        self.assertEqual(
            schedules[0].schedule_id,
            "schedule-001",
        )

        self.assertEqual(
            schedules[1].schedule_id,
            "schedule-002",
        )

    def test_list_due_returns_due_schedules(self):
        scheduled_for = self._scheduled_time()

        self.service.create_schedule(
            "schedule-001",
            "prod-001",
            ScheduleType.PUBLICATION,
            scheduled_for,
        )

        due = self.service.list_due(
            scheduled_for + timedelta(minutes=1)
        )

        self.assertEqual(
            len(due),
            1,
        )

        self.assertEqual(
            due[0].schedule_id,
            "schedule-001",
        )

    def test_list_due_excludes_future_schedules(self):
        scheduled_for = self._scheduled_time()

        self.service.create_schedule(
            "schedule-001",
            "prod-001",
            ScheduleType.PUBLICATION,
            scheduled_for,
        )

        due = self.service.list_due(
            scheduled_for - timedelta(minutes=1)
        )

        self.assertEqual(
            due,
            [],
        )

    def test_list_due_excludes_completed_schedules(self):
        scheduled_for = self._scheduled_time()

        self.service.create_schedule(
            "schedule-001",
            "prod-001",
            ScheduleType.PUBLICATION,
            scheduled_for,
        )

        self.service.activate(
            "schedule-001"
        )

        self.service.complete(
            "schedule-001"
        )

        due = self.service.list_due(
            scheduled_for + timedelta(hours=1)
        )

        self.assertEqual(
            due,
            [],
        )

    def test_repository_update_status_returns_updated_slot(self):
        self.service.create_schedule(
            "schedule-001",
            "prod-001",
            ScheduleType.PUBLICATION,
            self._scheduled_time(),
        )

        updated = self.repository.update_status(
            "schedule-001",
            ScheduleStatus.ACTIVE,
        )

        self.assertEqual(
            updated.status,
            ScheduleStatus.ACTIVE,
        )

    def test_repository_update_missing_schedule_is_rejected(self):
        with self.assertRaises(KeyError):
            self.repository.update_status(
                "missing-schedule",
                ScheduleStatus.ACTIVE,
            )

    def test_event_repository_round_trip(self):
        self.service.create_schedule(
            "schedule-001",
            "prod-001",
            ScheduleType.PUBLICATION,
            self._scheduled_time(),
        )

        event_repository = ScheduleEventRepository(
            self.connection
        )

        event = ScheduleEvent(
            event_id="event-001",
            schedule_id="schedule-001",
            from_status="PLANNED",
            to_status="ACTIVE",
            occurred_at=self._scheduled_time(),
            reason="Schedule activated.",
        )

        event_repository.create(
            event
        )

        events = event_repository.list_for_schedule(
            "schedule-001"
        )

        self.assertEqual(
            len(events),
            1,
        )

        self.assertEqual(
            events[0].event_id,
            "event-001",
        )

        self.assertEqual(
            events[0].from_status,
            "PLANNED",
        )

        self.assertEqual(
            events[0].to_status,
            "ACTIVE",
        )

    def test_event_requires_reason(self):
        with self.assertRaises(ValueError):
            ScheduleEvent(
                event_id="event-001",
                schedule_id="schedule-001",
                from_status="PLANNED",
                to_status="ACTIVE",
                occurred_at=self._scheduled_time(),
                reason="",
            )


if __name__ == "__main__":
    unittest.main()
