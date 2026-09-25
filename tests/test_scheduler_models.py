"""
Tests for Shadow Files scheduler-domain models.

Uses the project's unittest-based test runner.
"""

import unittest
from datetime import datetime, timedelta, timezone

from app.scheduler.models import (
    ScheduleSlot,
    ScheduleStatus,
    ScheduleType,
)


UTC = timezone.utc


class SchedulerModelTests(unittest.TestCase):

    def _scheduled_time(self):
        return datetime(
            2026,
            10,
            6,
            20,
            0,
            tzinfo=UTC,
        )

    def test_valid_schedule_slot_is_accepted(self):
        scheduled_for = self._scheduled_time()

        slot = ScheduleSlot(
            schedule_id="schedule-001",
            production_id="prod-001",
            schedule_type=ScheduleType.PUBLICATION,
            scheduled_for=scheduled_for,
            deadline=scheduled_for - timedelta(hours=24),
            timezone_name="UTC",
        )

        self.assertEqual(
            slot.schedule_id,
            "schedule-001",
        )

        self.assertEqual(
            slot.status,
            ScheduleStatus.PLANNED,
        )

        self.assertEqual(
            slot.schedule_type,
            ScheduleType.PUBLICATION,
        )

    def test_schedule_requires_timezone_aware_time(self):
        scheduled_for = datetime(
            2026,
            10,
            6,
            20,
            0,
        )

        with self.assertRaises(ValueError):
            ScheduleSlot(
                schedule_id="schedule-001",
                production_id="prod-001",
                schedule_type=ScheduleType.PUBLICATION,
                scheduled_for=scheduled_for,
            )

    def test_schedule_rejects_naive_deadline(self):
        scheduled_for = self._scheduled_time()

        with self.assertRaises(ValueError):
            ScheduleSlot(
                schedule_id="schedule-001",
                production_id="prod-001",
                schedule_type=ScheduleType.PUBLICATION,
                scheduled_for=scheduled_for,
                deadline=datetime(
                    2026,
                    10,
                    5,
                    20,
                    0,
                ),
            )

    def test_deadline_cannot_follow_scheduled_time(self):
        scheduled_for = self._scheduled_time()

        with self.assertRaises(ValueError):
            ScheduleSlot(
                schedule_id="schedule-001",
                production_id="prod-001",
                schedule_type=ScheduleType.PUBLICATION,
                scheduled_for=scheduled_for,
                deadline=scheduled_for + timedelta(hours=1),
            )

    def test_schedule_requires_timezone_name(self):
        with self.assertRaises(ValueError):
            ScheduleSlot(
                schedule_id="schedule-001",
                production_id="prod-001",
                schedule_type=ScheduleType.PUBLICATION,
                scheduled_for=self._scheduled_time(),
                timezone_name="",
            )

    def test_invalid_schedule_type_is_rejected(self):
        with self.assertRaises(TypeError):
            ScheduleSlot(
                schedule_id="schedule-001",
                production_id="prod-001",
                schedule_type="PUBLICATION",
                scheduled_for=self._scheduled_time(),
            )

    def test_invalid_schedule_status_is_rejected(self):
        with self.assertRaises(TypeError):
            ScheduleSlot(
                schedule_id="schedule-001",
                production_id="prod-001",
                schedule_type=ScheduleType.PUBLICATION,
                scheduled_for=self._scheduled_time(),
                status="PLANNED",
            )


if __name__ == "__main__":
    unittest.main()
