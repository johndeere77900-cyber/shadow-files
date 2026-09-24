"""
Shadow Files conversation-layer tests.

Phase 9 verifies deterministic intent recognition and confirms that
parsing a message does not execute any operation.
"""

import unittest

from app.conversation.intents import IntentType
from app.conversation.parser import IntentParser


class ConversationParserTests(unittest.TestCase):
    """Test natural-language intent parsing."""

    def setUp(self) -> None:
        self.parser = IntentParser()

    def test_status_request_is_recognized(self) -> None:
        intent = self.parser.parse(
            "How are we doing?"
        )

        self.assertEqual(
            intent.intent_type,
            IntentType.STATUS,
        )

    def test_case_status_request_is_recognized(self) -> None:
        intent = self.parser.parse(
            "What's holding up video three?"
        )

        self.assertEqual(
            intent.intent_type,
            IntentType.CASE_STATUS,
        )

    def test_continue_case_request_is_recognized(self) -> None:
        intent = self.parser.parse(
            "Continue the case we were researching yesterday."
        )

        self.assertEqual(
            intent.intent_type,
            IntentType.CONTINUE_CASE,
        )

    def test_schedule_change_is_recognized(self) -> None:
        intent = self.parser.parse(
            "Move the fourth video to next Tuesday."
        )

        self.assertEqual(
            intent.intent_type,
            IntentType.SCHEDULE_CHANGE,
        )

    def test_research_request_is_recognized(self) -> None:
        intent = self.parser.parse(
            "Research this case."
        )

        self.assertEqual(
            intent.intent_type,
            IntentType.RESEARCH,
        )

    def test_analysis_request_is_recognized(self) -> None:
        intent = self.parser.parse(
            "Analyze this case."
        )

        self.assertEqual(
            intent.intent_type,
            IntentType.ANALYZE,
        )

    def test_schedule_request_is_recognized(self) -> None:
        intent = self.parser.parse(
            "Show me this month's schedule."
        )

        self.assertEqual(
            intent.intent_type,
            IntentType.SHOW_SCHEDULE,
        )

    def test_help_request_is_recognized(self) -> None:
        intent = self.parser.parse(
            "Help."
        )

        self.assertEqual(
            intent.intent_type,
            IntentType.HELP,
        )

    def test_unknown_request_is_rejected_as_unknown(self) -> None:
        intent = self.parser.parse(
            "Do something completely unexpected."
        )

        self.assertEqual(
            intent.intent_type,
            IntentType.UNKNOWN,
        )
        self.assertEqual(
            intent.confidence,
            0.0,
        )

    def test_empty_request_is_unknown(self) -> None:
        intent = self.parser.parse("")

        self.assertEqual(
            intent.intent_type,
            IntentType.UNKNOWN,
        )
        self.assertEqual(
            intent.confidence,
            0.0,
        )

    def test_parser_preserves_original_text(self) -> None:
        text = "  How are we doing?  "

        intent = self.parser.parse(text)

        self.assertEqual(
            intent.raw_text,
            text,
        )


if __name__ == "__main__":
    unittest.main()
