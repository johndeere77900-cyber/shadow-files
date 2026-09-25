"""
Tests for Shadow Files scheduler calendar and recurrence utilities.
"""

import unittest
from datetime import datetime, timedelta, timezone

from app.scheduler.calendar import (
    calculate_deadline,
    is_due,
    is_overdue,
    next_weekly_occurrence,
    validate_schedule_window,
)
from app.scheduler.models import (
    ScheduleSlot,
    ScheduleStatus,
    ScheduleType,
)
from app.scheduler.recurrence import (
    WeeklyScheduleRule,
    generate_weekly_occurrences,
)


UTC = timezone.utc


class SchedulerCalendarRecurrenceTests(unittest.TestCase):

    def _start(self):
        return datetime(
            2026,
            10,
            5,
            12,
            30,
            tzinfo=UTC,
        )

    def _slot(self, scheduled_for, status=ScheduleStatus.PLANNED):
        return ScheduleSlot(
            schedule_id="schedule-001",
            production_id="prod-001",
            schedule_type=ScheduleType.PUBLICATION,
            scheduled_for=scheduled_for,
            status=status,
        )

    def test_validate_schedule_window_accepts_valid_times(self):
        scheduled_for = self._start()

        validate_schedule_window(
            scheduled_for,
            scheduled_for - timedelta(hours=2),
        )

    def test_validate_schedule_window_rejects_naive_scheduled_time(self):
        with self.assertRaises(ValueError):
            validate_schedule_window(
                datetime(2026, 10, 5, 12, 30)
            )

    def test_validate_schedule_window_rejects_naive_deadline(self):
        scheduled_for = self._start()

        with self.assertRaises(ValueError):
            validate_schedule_window(
                scheduled_for,
                datetime(2026, 10, 5, 10, 30),
            )

    def test_validate_schedule_window_rejects_late_deadline(self):
        scheduled_for = self._start()

        with self.assertRaises(ValueError):
            validate_schedule_window(
                scheduled_for,
                scheduled_for + timedelta(minutes=1),
            )

    def test_is_due_when_scheduled_time_has_arrived(self):
        scheduled_for = self._start()

        slot = self._slot(scheduled_for)

        self.assertTrue(
            is_due(
                slot,
                scheduled_for,
            )
        )

    def test_is_not_due_before_scheduled_time(self):
        scheduled_for = self._start()

        slot = self._slot(scheduled_for)

        self.assertFalse(
            is_due(
                slot,
                scheduled_for - timedelta(minutes=1),
            )
        )

    def test_completed_slot_is_not_due(self):
        scheduled_for = self._start()

        slot = self._slot(
            scheduled_for,
            ScheduleStatus.COMPLETED,
        )

        self.assertFalse(
            is_due(
                slot,
                scheduled_for + timedelta(hours=1),
            )
        )

    def test_is_overdue_after_scheduled_time(self):
        scheduled_for = self._start()

        slot = self._slot(scheduled_for)

        self.assertTrue(
            is_overdue(
                slot,
                scheduled_for + timedelta(minutes=1),
            )
        )

    def test_completed_slot_is_not_overdue(self):
        scheduled_for = self._start()

        slot = self._slot(
            scheduled_for,
            ScheduleStatus.COMPLETED,
        )

        self.assertFalse(
            is_overdue(
                slot,
                scheduled_for + timedelta(hours=1),
            )
        )

    def test_naive_now_is_rejected_by_is_due(self):
        slot = self._slot(self._start())

        with self.assertRaises(ValueError):
            is_due(
                slot,
                datetime(2026, 10, 5, 12, 30),
            )

    def test_naive_now_is_rejected_by_is_overdue(self):
        slot = self._slot(self._start())

        with self.assertRaises(ValueError):
            is_overdue(
                slot,
                datetime(2026, 10, 5, 12, 31),
            )

    def test_calculate_deadline(self):
        scheduled_for = self._start()

        deadline = calculate_deadline(
            scheduled_for,
            24,
        )

        self.assertEqual(
            deadline,
            scheduled_for - timedelta(hours=24),
        )

    def test_negative_preparation_minutes_are_rejected(self):
        with self.assertRaises(ValueError):
            calculate_deadline(
                self._start(),
                -1,
            )

    def test_next_weekly_occurrence_returns_same_day_when_future(self):
        start = datetime(
            2026,
            10,
            5,
            10,
            0,
            tzinfo=UTC,
        )

        result = next_weekly_occurrence(
            start,
            weekday=0,
            hour=20,
            minute=0,
        )

        self.assertEqual(
            result,
            datetime(
                2026,
                10,
                5,
                20,
                0,
                tzinfo=UTC,
            ),
        )

    def test_next_weekly_occurrence_moves_to_next_week_when_time_passed(self):
        start = datetime(
            2026,
            10,
            5,
            21,
            0,
            tzinfo=UTC,
        )

        result = next_weekly_occurrence(
            start,
            weekday=0,
            hour=20,
            minute=0,
        )

        self.assertEqual(
            result,
            datetime(
                2026,
                10,
                12,
                20,
                0,
                tzinfo=UTC,
            ),
        )

    def test_next_weekly_occurrence_rejects_invalid_weekday(self):
        with self.assertRaises(ValueError):
            next_weekly_occurrence(
                self._start(),
                weekday=7,
                hour=20,
            )

    def test_next_weekly_occurrence_rejects_invalid_hour(self):
        with self.assertRaises(ValueError):
            next_weekly_occurrence(
                self._start(),
                weekday=1,
                hour=24,
            )

    def test_recurrence_rule_validates_values(self):
        rule = WeeklyScheduleRule(
            weekday=1,
            hour=20,
            minute=30,
            occurrences=4,
        )

        self.assertEqual(
            rule.occurrences,
            4,
        )

    def test_recurrence_rule_rejects_invalid_weekday(self):
        with self.assertRaises(ValueError):
            WeeklyScheduleRule(
                weekday=7,
                hour=20,
            )

    def test_recurrence_rule_rejects_invalid_hour(self):
        with self.assertRaises(ValueError):
            WeeklyScheduleRule(
                weekday=1,
                hour=24,
            )

    def test_recurrence_rule_rejects_zero_occurrences(self):
        with self.assertRaises(ValueError):
            WeeklyScheduleRule(
                weekday=1,
                hour=20,
                occurrences=0,
            )

    def test_generate_weekly_occurrences(self):
        start = datetime(
            2026,
            10,
            5,
            10,
            0,
            tzinfo=UTC,
        )

        rule = WeeklyScheduleRule(
            weekday=1,
            hour=20,
            minute=0,
            occurrences=4,
        )

        occurrences = generate_weekly_occurrences(
            start,
            rule,
        )

        self.assertEqual(
            len(occurrences),
            4,
        )

        self.assertEqual(
            occurrences[0],
            datetime(
                2026,
                10,
                6,
                20,
                0,
                tzinfo=UTC,
            ),
        )

        self.assertEqual(
            occurrences[1],
            occurrences[0] + timedelta(weeks=1),
        )

        self.assertEqual(
            occurrences[2],
            occurrences[0] + timedelta(weeks=2),
        )

        self.assertEqual(
            occurrences[3],
            occurrences[0] + timedelta(weeks=3),
        )

    def test_generate_weekly_occurrences_requires_timezone_aware_start(self):
        rule = WeeklyScheduleRule(
            weekday=1,
            hour=20,
        )

        with self.assertRaises(ValueError):
            generate_weekly_occurrences(
                datetime(2026, 10, 5, 10, 0),
                rule,
            )


if __name__ == "__main__":
    unittest.main()
