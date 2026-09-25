"""
Tests for Shadow Files scheduler-set constraints.
"""

import unittest
from datetime import datetime, timedelta, timezone

from app.scheduler.constraints import (
    ScheduleConstraintError,
    validate_deadlines,
    validate_no_duplicate_type_for_production,
    validate_schedule_set,
    validate_slot_order,
    validate_unique_schedule_ids,
)
from app.scheduler.models import (
    ScheduleSlot,
    ScheduleType,
)


UTC = timezone.utc


class SchedulerConstraintTests(unittest.TestCase):

    def _time(self, hour):
        return datetime(
            2026,
            10,
            6,
            hour,
            0,
            tzinfo=UTC,
        )

    def _slot(
        self,
        schedule_id,
        production_id,
        schedule_type,
        scheduled_for,
        deadline=None,
    ):
        return ScheduleSlot(
            schedule_id=schedule_id,
            production_id=production_id,
            schedule_type=schedule_type,
            scheduled_for=scheduled_for,
            deadline=deadline,
        )

    def test_valid_production_and_publication_order(self):
        slots = [
            self._slot(
                "production-001",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(18),
            ),
            self._slot(
                "publication-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(20),
            ),
        ]

        validate_slot_order(slots)

    def test_publication_before_production_is_rejected(self):
        slots = [
            self._slot(
                "production-001",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(20),
            ),
            self._slot(
                "publication-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(18),
            ),
        ]

        with self.assertRaises(
            ScheduleConstraintError
        ):
            validate_slot_order(slots)

    def test_publication_without_production_is_allowed(self):
        slots = [
            self._slot(
                "publication-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(20),
            ),
        ]

        validate_slot_order(slots)

    def test_unique_schedule_ids_are_accepted(self):
        slots = [
            self._slot(
                "schedule-001",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(18),
            ),
            self._slot(
                "schedule-002",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(20),
            ),
        ]

        validate_unique_schedule_ids(slots)

    def test_duplicate_schedule_ids_are_rejected(self):
        slots = [
            self._slot(
                "schedule-001",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(18),
            ),
            self._slot(
                "schedule-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(20),
            ),
        ]

        with self.assertRaises(
            ScheduleConstraintError
        ):
            validate_unique_schedule_ids(slots)

    def test_different_schedule_types_for_same_production_are_allowed(self):
        slots = [
            self._slot(
                "production-001",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(18),
            ),
            self._slot(
                "publication-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(20),
            ),
        ]

        validate_no_duplicate_type_for_production(slots)

    def test_duplicate_production_schedule_type_is_rejected(self):
        slots = [
            self._slot(
                "production-001",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(18),
            ),
            self._slot(
                "production-002",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(19),
            ),
        ]

        with self.assertRaises(
            ScheduleConstraintError
        ):
            validate_no_duplicate_type_for_production(slots)

    def test_duplicate_publication_schedule_type_is_rejected(self):
        slots = [
            self._slot(
                "publication-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(18),
            ),
            self._slot(
                "publication-002",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(20),
            ),
        ]

        with self.assertRaises(
            ScheduleConstraintError
        ):
            validate_no_duplicate_type_for_production(slots)

    def test_valid_deadline_is_accepted(self):
        scheduled_for = self._time(20)

        slots = [
            self._slot(
                "schedule-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                scheduled_for,
                deadline=scheduled_for - timedelta(hours=2),
            ),
        ]

        validate_deadlines(slots)

    def test_deadline_after_scheduled_time_is_rejected(self):
        scheduled_for = self._time(20)

        slots = [
            self._slot(
                "schedule-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                scheduled_for,
                deadline=scheduled_for + timedelta(hours=1),
            ),
        ]

        with self.assertRaises(
            ScheduleConstraintError
        ):
            validate_deadlines(slots)

    def test_missing_deadline_is_allowed(self):
        slots = [
            self._slot(
                "schedule-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(20),
            ),
        ]

        validate_deadlines(slots)

    def test_complete_schedule_set_is_valid(self):
        scheduled_for = self._time(20)

        slots = [
            self._slot(
                "production-001",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(18),
                deadline=self._time(16),
            ),
            self._slot(
                "publication-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                scheduled_for,
                deadline=self._time(18),
            ),
        ]

        validate_schedule_set(slots)

    def test_complete_schedule_set_rejects_duplicate_ids(self):
        slots = [
            self._slot(
                "same-id",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(18),
            ),
            self._slot(
                "same-id",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(20),
            ),
        ]

        with self.assertRaises(
            ScheduleConstraintError
        ):
            validate_schedule_set(slots)

    def test_complete_schedule_set_rejects_duplicate_types(self):
        slots = [
            self._slot(
                "production-001",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(18),
            ),
            self._slot(
                "production-002",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(19),
            ),
        ]

        with self.assertRaises(
            ScheduleConstraintError
        ):
            validate_schedule_set(slots)

    def test_complete_schedule_set_rejects_bad_order(self):
        slots = [
            self._slot(
                "production-001",
                "prod-001",
                ScheduleType.PRODUCTION,
                self._time(20),
            ),
            self._slot(
                "publication-001",
                "prod-001",
                ScheduleType.PUBLICATION,
                self._time(18),
            ),
        ]

        with self.assertRaises(
            ScheduleConstraintError
        ):
            validate_schedule_set(slots)


if __name__ == "__main__":
    unittest.main()
