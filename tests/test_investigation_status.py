"""
Shadow Files Phase 12 research-status transition tests.
"""

import unittest

from app.investigation.models import ResearchStatus
from app.investigation.status import (
    InvalidResearchTransition,
    can_transition,
    transition,
)


class InvestigationStatusTests(unittest.TestCase):
    """Verify investigation lifecycle rules."""

    def test_not_started_can_begin_research(self) -> None:
        self.assertTrue(
            can_transition(
                ResearchStatus.NOT_STARTED,
                ResearchStatus.RESEARCHING,
            )
        )

    def test_researching_can_enter_evidence_review(self) -> None:
        self.assertTrue(
            can_transition(
                ResearchStatus.RESEARCHING,
                ResearchStatus.EVIDENCE_REVIEW,
            )
        )

    def test_evidence_review_can_become_verified(self) -> None:
        self.assertTrue(
            can_transition(
                ResearchStatus.EVIDENCE_REVIEW,
                ResearchStatus.VERIFIED,
            )
        )

    def test_research_can_be_marked_incomplete(self) -> None:
        self.assertTrue(
            can_transition(
                ResearchStatus.RESEARCHING,
                ResearchStatus.INCOMPLETE,
            )
        )

    def test_incomplete_can_return_to_research(self) -> None:
        self.assertTrue(
            can_transition(
                ResearchStatus.INCOMPLETE,
                ResearchStatus.RESEARCHING,
            )
        )

    def test_blocked_can_return_to_research(self) -> None:
        self.assertTrue(
            can_transition(
                ResearchStatus.BLOCKED,
                ResearchStatus.RESEARCHING,
            )
        )

    def test_verified_cannot_move_backwards(self) -> None:
        self.assertFalse(
            can_transition(
                ResearchStatus.VERIFIED,
                ResearchStatus.RESEARCHING,
            )
        )

    def test_invalid_transition_is_rejected(self) -> None:
        with self.assertRaises(InvalidResearchTransition):
            transition(
                ResearchStatus.NOT_STARTED,
                ResearchStatus.VERIFIED,
            )

    def test_valid_transition_returns_target(self) -> None:
        result = transition(
            ResearchStatus.NOT_STARTED,
            ResearchStatus.RESEARCHING,
        )

        self.assertEqual(
            result,
            ResearchStatus.RESEARCHING,
        )


if __name__ == "__main__":
    unittest.main()
