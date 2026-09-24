"""
Shadow Files conversation handler.

The handler connects parsing and validation while deliberately stopping
before execution. This preserves the separation between understanding
a command and actually performing it.
"""

from dataclasses import dataclass

from app.conversation.intents import Intent
from app.conversation.parser import IntentParser
from app.conversation.validation import (
    IntentValidator,
    ValidationResult,
)


@dataclass(frozen=True)
class ConversationResult:
    """Result of processing a conversational message."""

    intent: Intent
    validation: ValidationResult


class ConversationHandler:
    """Parse and validate conversational requests."""

    def __init__(
        self,
        parser: IntentParser | None = None,
        validator: IntentValidator | None = None,
    ) -> None:
        self.parser = parser or IntentParser()
        self.validator = validator or IntentValidator()

    def handle(
        self,
        text: str,
    ) -> ConversationResult:
        """
        Parse and validate a message.

        No business operation is executed here.
        """

        intent = self.parser.parse(text)

        validation = self.validator.validate(
            intent
        )

        return ConversationResult(
            intent=intent,
            validation=validation,
        )
