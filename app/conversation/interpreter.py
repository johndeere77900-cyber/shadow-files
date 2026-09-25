"""
Shadow Files conversation interpreter compatibility layer.

The canonical deterministic language parser is IntentParser.

This module exists as a compatibility adapter for callers that expect a
ConversationInterpreter interface. It must not maintain a second set of
natural-language parsing rules.
"""

from app.conversation.models import (
    ConversationIntent,
    ConversationIntentResult,
    ConversationMode,
)
from app.conversation.intents import IntentType
from app.conversation.parser import IntentParser


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
            IntentType.STATUS: (
                ConversationMode.INFORMATION_REQUEST,
                ConversationIntent.CHECK_STATUS,
            ),
            IntentType.CASE_STATUS: (
                ConversationMode.INFORMATION_REQUEST,
                ConversationIntent.CHECK_STATUS,
            ),
            IntentType.CONTINUE_CASE: (
                ConversationMode.EXECUTION_REQUEST,
                ConversationIntent.CONTINUE_WORK,
            ),
            IntentType.SCHEDULE_CHANGE: (
                ConversationMode.EXECUTION_REQUEST,
                ConversationIntent.CHANGE_SCHEDULE,
            ),
            IntentType.RESEARCH: (
                ConversationMode.EXECUTION_REQUEST,
                ConversationIntent.START_RESEARCH,
            ),
            IntentType.ANALYZE: (
                ConversationMode.EXECUTION_REQUEST,
                ConversationIntent.DISCUSS_CASE,
            ),
            IntentType.SHOW_SCHEDULE: (
                ConversationMode.INFORMATION_REQUEST,
                ConversationIntent.CHECK_STATUS,
            ),
            IntentType.HELP: (
                ConversationMode.INFORMATION_REQUEST,
                ConversationIntent.ASK_CAPABILITIES,
            ),
            IntentType.UNKNOWN: (
                ConversationMode.CLARIFICATION_REQUIRED,
                ConversationIntent.UNKNOWN,
            ),
        }

        mode, conversation_intent = mapping.get(
            intent.intent_type,
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
