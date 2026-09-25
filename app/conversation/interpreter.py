"""
Shadow Files conversation interpreter compatibility layer.

The canonical deterministic language parser is IntentParser.

This module exists as a compatibility adapter for callers that expect a
ConversationInterpreter interface. It must not maintain a second set of
natural-language parsing rules.
"""

from app.conversation.intents import IntentParser
from app.conversation.models import (
    ConversationIntent,
    ConversationIntentResult,
    ConversationMode,
)


class ConversationInterpreter:
    """
    Compatibility adapter around the canonical IntentParser.

    Natural-language recognition belongs to IntentParser. This class only
    converts its result into the conversation-layer representation.
    """

    def __init__(
        self,
        parser: IntentParser | None = None,
    ) -> None:
        self._parser = parser or IntentParser()

    def interpret(
        self,
        text: str,
    ) -> ConversationIntentResult:
        """Interpret text using the canonical IntentParser."""

        intent = self._parser.parse(text)

        mapping = {
            "STATUS": (
                ConversationMode.INFORMATION_REQUEST,
                ConversationIntent.CHECK_STATUS,
            ),
            "CASE_STATUS": (
                ConversationMode.INFORMATION_REQUEST,
                ConversationIntent.CHECK_STATUS,
            ),
            "CONTINUE_CASE": (
                ConversationMode.EXECUTION_REQUEST,
                ConversationIntent.CONTINUE_WORK,
            ),
            "SCHEDULE_CHANGE": (
                ConversationMode.EXECUTION_REQUEST,
                ConversationIntent.CONTINUE_WORK,
            ),
            "RESEARCH": (
                ConversationMode.EXECUTION_REQUEST,
                ConversationIntent.START_RESEARCH,
            ),
            "ANALYZE": (
                ConversationMode.EXECUTION_REQUEST,
                ConversationIntent.DISCUSS_CASE,
            ),
            "SHOW_SCHEDULE": (
                ConversationMode.INFORMATION_REQUEST,
                ConversationIntent.CHECK_STATUS,
            ),
            "HELP": (
                ConversationMode.INFORMATION_REQUEST,
                ConversationIntent.ASK_CAPABILITIES,
            ),
            "UNKNOWN": (
                ConversationMode.CLARIFICATION_REQUIRED,
                ConversationIntent.UNKNOWN,
            ),
        }

        mode, conversation_intent = mapping.get(
            intent.intent_type.value,
            (
                ConversationMode.CONVERSATION,
                ConversationIntent.GENERAL_CONVERSATION,
            ),
        )

        return ConversationIntentResult(
            mode=mode,
            intent=conversation_intent,
            confidence=intent.confidence,
            target=intent.target,
            parameters=intent.parameters,
        )
