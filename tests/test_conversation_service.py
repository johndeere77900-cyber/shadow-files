"""
Shadow Files conversation service tests.

These tests verify conversational context, candidate selection,
intent conversion, and the boundary that conversation interpretation
does not execute business operations.
"""

import unittest

from app.conversation.models import (
    ConversationIntent,
    ConversationMode,
)
from app.conversation.service import ConversationService


class ConversationServiceTests(unittest.TestCase):
    """Test the conversation service."""

    def setUp(self) -> None:
        self.service = ConversationService()

    def test_status_request_becomes_information_request(self) -> None:
        result = self.service.handle(
            "chat-1",
            "How are we doing?",
        )

        self.assertEqual(
            result.interpretation.mode,
            ConversationMode.INFORMATION_REQUEST,
        )
        self.assertEqual(
            result.interpretation.intent,
            ConversationIntent.CHECK_STATUS,
        )

    def test_research_request_is_execution_request(self) -> None:
        result = self.service.handle(
            "chat-1",
            "Research this case.",
        )

        self.assertEqual(
            result.interpretation.mode,
            ConversationMode.EXECUTION_REQUEST,
        )
        self.assertEqual(
            result.interpretation.intent,
            ConversationIntent.START_RESEARCH,
        )

    def test_schedule_change_maps_to_change_schedule(self) -> None:
        result = self.service.handle(
            "chat-1",
            "Move the fourth video to next Tuesday.",
        )

        self.assertEqual(
            result.interpretation.mode,
            ConversationMode.EXECUTION_REQUEST,
        )
        self.assertEqual(
            result.interpretation.intent,
            ConversationIntent.CHANGE_SCHEDULE,
        )

    def test_candidate_number_selects_candidate(self) -> None:
        self.service.set_candidates(
            "chat-1",
            [
                "case-1",
                "case-2",
                "case-3",
            ],
        )

        result = self.service.handle(
            "chat-1",
            "Let's use number 3.",
        )

        self.assertEqual(
            result.interpretation.intent,
            ConversationIntent.SELECT_CASE,
        )
        self.assertEqual(
            result.interpretation.mode,
            ConversationMode.CONVERSATION,
        )
        self.assertEqual(
            result.interpretation.target,
            "case-3",
        )
        self.assertEqual(
            result.context.active_case_id,
            "case-3",
        )

    def test_invalid_candidate_number_requires_clarification(self) -> None:
        self.service.set_candidates(
            "chat-1",
            [
                "case-1",
                "case-2",
            ],
        )

        result = self.service.handle(
            "chat-1",
            "Let's use number 5.",
        )

        self.assertEqual(
            result.interpretation.intent,
            ConversationIntent.SELECT_CASE,
        )
        self.assertEqual(
            result.interpretation.mode,
            ConversationMode.CLARIFICATION_REQUIRED,
        )
        self.assertEqual(
            result.interpretation.target,
            "5",
        )

    def test_context_is_preserved_between_turns(self) -> None:
        self.service.set_candidates(
            "chat-1",
            [
                "case-1",
                "case-2",
            ],
        )

        self.service.handle(
            "chat-1",
            "Let's use number 2.",
        )

        context = self.service.get_context("chat-1")

        self.assertEqual(
            context.active_case_id,
            "case-2",
        )
        self.assertGreaterEqual(
            len(context.turns),
            2,
        )

    def test_conversations_have_separate_contexts(self) -> None:
        self.service.set_active_case(
            "chat-1",
            "case-1",
        )
        self.service.set_active_case(
            "chat-2",
            "case-2",
        )

        self.assertEqual(
            self.service.get_context("chat-1").active_case_id,
            "case-1",
        )
        self.assertEqual(
            self.service.get_context("chat-2").active_case_id,
            "case-2",
        )

    def test_unknown_request_requires_clarification(self) -> None:
        result = self.service.handle(
            "chat-1",
            "Something completely unexpected.",
        )

        self.assertEqual(
            result.interpretation.mode,
            ConversationMode.CLARIFICATION_REQUIRED,
        )
        self.assertEqual(
            result.interpretation.intent,
            ConversationIntent.GENERAL_CONVERSATION,
        )

    def test_service_does_not_execute_business_operation(self) -> None:
        result = self.service.handle(
            "chat-1",
            "Research this case.",
        )

        self.assertEqual(
            result.interpretation.intent,
            ConversationIntent.START_RESEARCH,
        )

        # The service only interprets the request. No research result,
        # repository mutation, or external operation is performed here.
        self.assertIsNone(
            result.interpretation.target,
        )

    def test_clear_context_removes_conversation_state(self) -> None:
        self.service.set_active_case(
            "chat-1",
            "case-1",
        )

        self.service.clear_context("chat-1")

        context = self.service.get_context("chat-1")

        self.assertIsNone(
            context.active_case_id,
        )
        self.assertEqual(
            context.candidate_case_ids,
            [],
        )


if __name__ == "__main__":
    unittest.main()
