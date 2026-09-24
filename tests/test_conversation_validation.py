"""
Shadow Files conversation validation tests.
"""

import unittest

from app.conversation.handler import ConversationHandler
from app.conversation.intents import (
    Intent,
    IntentType,
)
from app.conversation.validation import (
    IntentValidator,
)


class IntentValidationTests(unittest.TestCase):
    """Test intent validation."""

    def setUp(self) -> None:
        self.validator = IntentValidator()

    def test_valid_intent_is_accepted(self) -> None:
        intent = Intent(
            intent_type=IntentType.STATUS,
            raw_text="How are we doing?",
        )

        result = self.validator.validate(
            intent
        )

        self.assertTrue(result.valid)
        self.assertEqual(
            result.reason,
            "",
        )

    def test_unknown_intent_is_rejected(self) -> None:
        intent = Intent(
            intent_type=IntentType.UNKNOWN,
            raw_text="Something unclear",
            confidence=0.0,
        )

        result = self.validator.validate(
            intent
        )

        self.assertFalse(result.valid)
        self.assertIn(
            "could not be understood",
            result.reason,
        )

    def test_empty_text_is_rejected(self) -> None:
        intent = Intent(
            intent_type=IntentType.STATUS,
            raw_text="",
        )

        result = self.validator.validate(
            intent
        )

        self.assertFalse(result.valid)
        self.assertIn(
            "empty",
            result.reason,
        )

    def test_invalid_confidence_is_rejected(self) -> None:
        intent = Intent(
            intent_type=IntentType.STATUS,
            raw_text="How are we doing?",
            confidence=1.5,
        )

        result = self.validator.validate(
            intent
        )

        self.assertFalse(result.valid)
        self.assertIn(
            "between 0 and 1",
            result.reason,
        )


class ConversationHandlerTests(unittest.TestCase):
    """Test parsing and validation together."""

    def setUp(self) -> None:
        self.handler = ConversationHandler()

    def test_handler_recognizes_valid_request(self) -> None:
        result = self.handler.handle(
            "How are we doing?"
        )

        self.assertTrue(
            result.validation.valid
        )
        self.assertEqual(
            result.intent.intent_type,
            IntentType.STATUS,
        )

    def test_handler_rejects_unknown_request(self) -> None:
        result = self.handler.handle(
            "Do something completely unexpected."
        )

        self.assertFalse(
            result.validation.valid
        )
        self.assertEqual(
            result.intent.intent_type,
            IntentType.UNKNOWN,
        )

    def test_handler_does_not_execute_operations(self) -> None:
        result = self.handler.handle(
            "Research this case."
        )

        self.assertTrue(
            result.validation.valid
        )

        # The handler only interprets the request.
        # No research job, database mutation, or provider call
        # is performed at this stage.
        self.assertEqual(
            result.intent.intent_type,
            IntentType.RESEARCH,
        )


if __name__ == "__main__":
    unittest.main()
