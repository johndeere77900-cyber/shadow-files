"""
Tests for Shadow Files production-status transitions.
"""

import unittest

from app.production.models import ProductionStatus
from app.production.status import (
    InvalidProductionTransition,
    allowed_transitions,
    validate_transition,
)


class ProductionStatusTests(unittest.TestCase):

    def test_not_started_can_begin_story_planning(self):
        validate_transition(
            ProductionStatus.NOT_STARTED,
            ProductionStatus.STORY_PLANNING,
        )

    def test_story_planning_can_begin_script_draft(self):
        validate_transition(
            ProductionStatus.STORY_PLANNING,
            ProductionStatus.SCRIPT_DRAFT,
        )

    def test_script_draft_can_enter_review(self):
        validate_transition(
            ProductionStatus.SCRIPT_DRAFT,
            ProductionStatus.SCRIPT_REVIEW,
        )

    def test_script_review_can_be_approved(self):
        validate_transition(
            ProductionStatus.SCRIPT_REVIEW,
            ProductionStatus.SCRIPT_APPROVED,
        )

    def test_approved_script_can_begin_scene_planning(self):
        validate_transition(
            ProductionStatus.SCRIPT_APPROVED,
            ProductionStatus.SCENE_PLANNING,
        )

    def test_scene_planning_can_begin_production(self):
        validate_transition(
            ProductionStatus.SCENE_PLANNING,
            ProductionStatus.PRODUCTION,
        )

    def test_production_can_enter_qc(self):
        validate_transition(
            ProductionStatus.PRODUCTION,
            ProductionStatus.QC,
        )

    def test_qc_can_enter_human_approval(self):
        validate_transition(
            ProductionStatus.QC,
            ProductionStatus.HUMAN_APPROVAL,
        )

    def test_human_approval_can_mark_ready(self):
        validate_transition(
            ProductionStatus.HUMAN_APPROVAL,
            ProductionStatus.READY,
        )

    def test_invalid_transition_is_rejected(self):
        with self.assertRaises(InvalidProductionTransition):
            validate_transition(
                ProductionStatus.NOT_STARTED,
                ProductionStatus.READY,
            )

    def test_ready_cannot_return_to_production(self):
        with self.assertRaises(InvalidProductionTransition):
            validate_transition(
                ProductionStatus.READY,
                ProductionStatus.PRODUCTION,
            )

    def test_cancelled_cannot_resume(self):
        with self.assertRaises(InvalidProductionTransition):
            validate_transition(
                ProductionStatus.CANCELLED,
                ProductionStatus.PRODUCTION,
            )

    def test_allowed_transitions_returns_frozenset(self):
        transitions = allowed_transitions(
            ProductionStatus.NOT_STARTED
        )

        self.assertIsInstance(
            transitions,
            frozenset,
        )

        self.assertIn(
            ProductionStatus.STORY_PLANNING,
            transitions,
        )

    def test_invalid_current_status_type_is_rejected(self):
        with self.assertRaises(TypeError):
            validate_transition(
                "NOT_STARTED",
                ProductionStatus.STORY_PLANNING,
            )

    def test_invalid_target_status_type_is_rejected(self):
        with self.assertRaises(TypeError):
            validate_transition(
                ProductionStatus.NOT_STARTED,
                "STORY_PLANNING",
            )


if __name__ == "__main__":
    unittest.main()
