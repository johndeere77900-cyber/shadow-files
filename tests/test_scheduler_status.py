"""
Tests for Shadow Files scheduler-status transitions.
"""

import unittest

from app.scheduler.models import ScheduleStatus
from app.scheduler.status import (
    InvalidScheduleTransition,
    allowed_transitions,
    validate_transition,
)


class SchedulerStatusTests(unittest.TestCase):

    def test_planned_can_become_active(self):
        validate_transition(
            ScheduleStatus.PLANNED,
            ScheduleStatus.ACTIVE,
        )

    def test_active_can_become_completed(self):
        validate_transition(
            ScheduleStatus.ACTIVE,
            ScheduleStatus.COMPLETED,
        )

    def test_active_can_become_missed(self):
        validate_transition(
            ScheduleStatus.ACTIVE,
            ScheduleStatus.MISSED,
        )

    def test_planned_can_be_blocked(self):
        validate_transition(
            ScheduleStatus.PLANNED,
            ScheduleStatus.BLOCKED,
        )

    def test_blocked_can_return_to_planned(self):
        validate_transition(
            ScheduleStatus.BLOCKED,
            ScheduleStatus.PLANNED,
        )

    def test_paused_can_become_active(self):
        validate_transition(
            ScheduleStatus.PAUSED,
            ScheduleStatus.ACTIVE,
        )

    def test_missed_can_be_replanned(self):
        validate_transition(
            ScheduleStatus.MISSED,
            ScheduleStatus.PLANNED,
        )

    def test_completed_cannot_resume(self):
        with self.assertRaises(
            InvalidScheduleTransition
        ):
            validate_transition(
                ScheduleStatus.COMPLETED,
                ScheduleStatus.ACTIVE,
            )

    def test_cancelled_cannot_resume(self):
        with self.assertRaises(
            InvalidScheduleTransition
        ):
            validate_transition(
                ScheduleStatus.CANCELLED,
                ScheduleStatus.PLANNED,
            )

    def test_planned_cannot_jump_to_completed(self):
        with self.assertRaises(
            InvalidScheduleTransition
        ):
            validate_transition(
                ScheduleStatus.PLANNED,
                ScheduleStatus.COMPLETED,
            )

    def test_invalid_current_status_type_is_rejected(self):
        with self.assertRaises(TypeError):
            validate_transition(
                "PLANNED",
                ScheduleStatus.ACTIVE,
            )

    def test_invalid_target_status_type_is_rejected(self):
        with self.assertRaises(TypeError):
            validate_transition(
                ScheduleStatus.PLANNED,
                "ACTIVE",
            )

    def test_allowed_transitions_returns_frozenset(self):
        transitions = allowed_transitions(
            ScheduleStatus.PLANNED
        )

        self.assertIsInstance(
            transitions,
            frozenset,
        )

        self.assertIn(
            ScheduleStatus.ACTIVE,
            transitions,
        )


if __name__ == "__main__":
    unittest.main()
