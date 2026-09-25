"""
Tests for Shadow Files scheduler planning and deadline utilities.
"""

import unittest
from datetime import datetime, timedelta, timezone

from app.scheduler.deadlines import (
    Deadline,
    build_standard_deadlines,
    calculate_deadline,
    is_deadline_overdue,
    is_deadline_reached,
)
from app.scheduler.planner import (
    ProductionSchedulePlan,
    PublicationSchedulePlan,
    build_production_schedule,
    build_publication_schedule,
    build_schedule_pair,
)


UTC = timezone.utc


class SchedulerPlannerDeadlineTests(unittest.TestCase):

    def _production_time(self):
        return datetime(
            2026,
            10,
            6,
            18,
            0,
            tzinfo=UTC,
        )

    def _publication_time(self):
        return datetime(
            2026,
            10,
            6,
            20,
            0,
            tzinfo=UTC,
        )

    def test_production_plan_accepts_valid_values(self):
        plan = ProductionSchedulePlan(
            production_id="prod-001",
            production_time=self._production_time(),
            preparation_hours=24,
            timezone_name="UTC",
        )

        self.assertEqual(
            plan.production_id,
            "prod-001",
        )

    def test_publication_plan_accepts_valid_values(self):
        plan = PublicationSchedulePlan(
            production_id="prod-001",
            publication_time=self._publication_time(),
            preparation_hours=24,
            timezone_name="UTC",
        )

        self.assertEqual(
            plan.production_id,
            "prod-001",
        )

    def test_production_plan_rejects_naive_time(self):
        with self.assertRaises(ValueError):
            ProductionSchedulePlan(
                production_id="prod-001",
                production_time=datetime(
                    2026,
                    10,
                    6,
                    18,
                    0,
                ),
            )

    def test_publication_plan_rejects_naive_time(self):
        with self.assertRaises(ValueError):
            PublicationSchedulePlan(
                production_id="prod-001",
                publication_time=datetime(
                    2026,
                    10,
                    6,
                    20,
                    0,
                ),
            )

    def test_negative_preparation_hours_are_rejected(self):
        with self.assertRaises(ValueError):
            ProductionSchedulePlan(
                production_id="prod-001",
                production_time=self._production_time(),
                preparation_hours=-1,
            )

    def test_build_production_schedule(self):
        plan = ProductionSchedulePlan(
            production_id="prod-001",
            production_time=self._production_time(),
            preparation_hours=24,
        )

        slot = build_production_schedule(
            plan,
            "schedule-production",
        )

        self.assertEqual(
            slot.production_id,
            "prod-001",
        )

        self.assertEqual(
            slot.schedule_type.value,
            "PRODUCTION",
        )

        self.assertEqual(
            slot.deadline,
            self._production_time() - timedelta(hours=24),
        )

    def test_build_publication_schedule(self):
        plan = PublicationSchedulePlan(
            production_id="prod-001",
            publication_time=self._publication_time(),
            preparation_hours=24,
        )

        slot = build_publication_schedule(
            plan,
            "schedule-publication",
        )

        self.assertEqual(
            slot.production_id,
            "prod-001",
        )

        self.assertEqual(
            slot.schedule_type.value,
            "PUBLICATION",
        )

        self.assertEqual(
            slot.deadline,
            self._publication_time() - timedelta(hours=24),
        )

    def test_schedule_pair_contains_production_and_publication(self):
        slots = build_schedule_pair(
            production_id="prod-001",
            production_time=self._production_time(),
            publication_time=self._publication_time(),
        )

        self.assertEqual(
            len(slots),
            2,
        )

        self.assertEqual(
            slots[0].schedule_type.value,
            "PRODUCTION",
        )

        self.assertEqual(
            slots[1].schedule_type.value,
            "PUBLICATION",
        )

    def test_schedule_pair_rejects_publication_before_production(self):
        with self.assertRaises(ValueError):
            build_schedule_pair(
                production_id="prod-001",
                production_time=self._publication_time(),
                publication_time=self._production_time(),
            )

    def test_calculate_deadline(self):
        target = self._publication_time()

        result = calculate_deadline(
            target,
            24,
        )

        self.assertEqual(
            result,
            target - timedelta(hours=24),
        )

    def test_deadline_requires_timezone_aware_time(self):
        with self.assertRaises(ValueError):
            calculate_deadline(
                datetime(
                    2026,
                    10,
                    6,
                    20,
                    0,
                ),
                24,
            )

    def test_deadline_rejects_negative_hours(self):
        with self.assertRaises(ValueError):
            calculate_deadline(
                self._publication_time(),
                -1,
            )

    def test_deadline_model_accepts_valid_values(self):
        deadline = Deadline(
            deadline_id="deadline-001",
            production_id="prod-001",
            due_at=self._publication_time(),
            label="QC complete",
        )

        self.assertFalse(
            deadline.completed
        )

    def test_deadline_requires_label(self):
        with self.assertRaises(ValueError):
            Deadline(
                deadline_id="deadline-001",
                production_id="prod-001",
                due_at=self._publication_time(),
                label="",
            )

    def test_deadline_requires_timezone_aware_due_time(self):
        with self.assertRaises(ValueError):
            Deadline(
                deadline_id="deadline-001",
                production_id="prod-001",
                due_at=datetime(
                    2026,
                    10,
                    6,
                    20,
                    0,
                ),
                label="QC complete",
            )

    def test_deadline_reached(self):
        deadline = Deadline(
            deadline_id="deadline-001",
            production_id="prod-001",
            due_at=self._publication_time(),
            label="QC complete",
        )

        self.assertTrue(
            is_deadline_reached(
                deadline,
                self._publication_time(),
            )
        )

    def test_deadline_not_reached_before_due_time(self):
        deadline = Deadline(
            deadline_id="deadline-001",
            production_id="prod-001",
            due_at=self._publication_time(),
            label="QC complete",
        )

        self.assertFalse(
            is_deadline_reached(
                deadline,
                self._publication_time() - timedelta(minutes=1),
            )
        )

    def test_incomplete_deadline_is_overdue(self):
        deadline = Deadline(
            deadline_id="deadline-001",
            production_id="prod-001",
            due_at=self._publication_time(),
            label="QC complete",
        )

        self.assertTrue(
            is_deadline_overdue(
                deadline,
                self._publication_time() + timedelta(minutes=1),
            )
        )

    def test_completed_deadline_is_not_overdue(self):
        deadline = Deadline(
            deadline_id="deadline-001",
            production_id="prod-001",
            due_at=self._publication_time(),
            label="QC complete",
            completed=True,
        )

        self.assertFalse(
            is_deadline_overdue(
                deadline,
                self._publication_time() + timedelta(hours=1),
            )
        )

    def test_standard_deadlines_are_created_in_order(self):
        deadlines = build_standard_deadlines(
            production_id="prod-001",
            publication_time=self._publication_time(),
        )

        self.assertEqual(
            len(deadlines),
            4,
        )

        self.assertLess(
            deadlines[0].due_at,
            deadlines[1].due_at,
        )

        self.assertLess(
            deadlines[1].due_at,
            deadlines[2].due_at,
        )

        self.assertLess(
            deadlines[2].due_at,
            deadlines[3].due_at,
        )

    def test_standard_deadlines_use_expected_labels(self):
        deadlines = build_standard_deadlines(
            production_id="prod-001",
            publication_time=self._publication_time(),
        )

        self.assertEqual(
            [deadline.label for deadline in deadlines],
            [
                "Research complete",
                "Script approved",
                "Production complete",
                "Quality control complete",
            ],
        )

    def test_standard_deadlines_reject_naive_publication_time(self):
        with self.assertRaises(ValueError):
            build_standard_deadlines(
                production_id="prod-001",
                publication_time=datetime(
                    2026,
                    10,
                    6,
                    20,
                    0,
                ),
            )

    def test_standard_deadlines_reject_negative_values(self):
        with self.assertRaises(ValueError):
            build_standard_deadlines(
                production_id="prod-001",
                publication_time=self._publication_time(),
                research_hours=-1,
            )


if __name__ == "__main__":
    unittest.main()
