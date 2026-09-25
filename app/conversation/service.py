"""
Shadow Files conversation service.

Coordinates the existing deterministic IntentParser with conversational
context. This layer understands conversation and references but does not
execute business operations.

Execution remains controlled by the command/application layers.
"""

from dataclasses import dataclass
import re

from app.conversation.context import ConversationContextStore
from app.conversation.intents import Intent, IntentType
from app.conversation.models import (
    ConversationContext,
    ConversationIntent,
    ConversationIntentResult,
    ConversationMode,
)
from app.conversation.parser import IntentParser


@dataclass(frozen=True)
class ConversationResponse:
    """Result returned by the conversation layer."""

    interpretation: ConversationIntentResult
    context: ConversationContext
    intent: Intent


class ConversationService:
    """
    Application-facing conversation service.

    The service:
    1. records the user's message,
    2. uses the existing IntentParser,
    3. resolves conversational references,
    4. records the interpretation,
    5. returns structured conversation information.

    It never executes the resulting action itself.
    """

    def __init__(
        self,
        parser: IntentParser | None = None,
        context_store: ConversationContextStore | None = None,
    ) -> None:
        self._parser = parser or IntentParser()
        self._context_store = (
            context_store or ConversationContextStore()
        )

    def handle(
        self,
        conversation_id: str,
        text: str,
    ) -> ConversationResponse:
        """Process one conversational turn."""

        context = self._context_store.get(conversation_id)

        context.add_turn(
            role="user",
            text=text,
        )

        intent = self._parser.parse(text)

        interpretation = self._convert_intent(
            intent=intent,
            context=context,
        )

        context.add_turn(
            role="shadow",
            text=self._describe_interpretation(
                interpretation
            ),
        )

        return ConversationResponse(
            interpretation=interpretation,
            context=context,
            intent=intent,
        )

    def set_candidates(
        self,
        conversation_id: str,
        case_ids: list[str],
    ) -> ConversationContext:
        """Store ordered candidate cases for later conversational references."""

        return self._context_store.set_candidate_cases(
            conversation_id,
            case_ids,
        )

    def set_active_case(
        self,
        conversation_id: str,
        case_id: str,
    ) -> ConversationContext:
        """Set the case currently being discussed."""

        return self._context_store.set_active_case(
            conversation_id,
            case_id,
        )

    def get_context(
        self,
        conversation_id: str,
    ) -> ConversationContext:
        """Return the current conversation context."""

        return self._context_store.get(
            conversation_id
        )

    def clear_context(
        self,
        conversation_id: str,
    ) -> None:
        """Clear one conversation's temporary context."""

        self._context_store.clear(
            conversation_id
        )

    def _convert_intent(
        self,
        intent: Intent,
        context: ConversationContext,
    ) -> ConversationIntentResult:
        """
        Convert the existing Intent model into the richer conversation
        result used by the conversational context layer.
        """

        candidate_number = self._candidate_number(
            intent.raw_text
        )

        if candidate_number is not None:
            if 1 <= candidate_number <= len(
                context.candidate_case_ids
            ):
                case_id = context.select_candidate(
                    candidate_number
                )

                return ConversationIntentResult(
                    mode=ConversationMode.CONVERSATION,
                    intent=ConversationIntent.SELECT_CASE,
                    confidence=intent.confidence,
                    target=case_id,
                    parameters=(
                        (
                            "candidate_number",
                            str(candidate_number),
                        ),
                    ),
                )

            return ConversationIntentResult(
                mode=ConversationMode.CLARIFICATION_REQUIRED,
                intent=ConversationIntent.SELECT_CASE,
                confidence=1.0,
                target=str(candidate_number),
            )

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
                ConversationMode.CONVERSATION,
                ConversationIntent.GENERAL_CONVERSATION,
            ),
        }

        mode, conversation_intent = mapping.get(
            intent.intent_type,
            (
                ConversationMode.CONVERSATION,
                ConversationIntent.GENERAL_CONVERSATION,
            ),
        )

        if intent.intent_type == IntentType.UNKNOWN:
            mode = ConversationMode.CLARIFICATION_REQUIRED

        return ConversationIntentResult(
            mode=mode,
            intent=conversation_intent,
            confidence=intent.confidence,
            target=intent.target,
            parameters=intent.parameters,
        )

    @staticmethod
    def _candidate_number(text: str) -> int | None:
        """Extract conversational references such as 'number 3'."""

        patterns = (
            r"\bnumber\s+(\d+)\b",
            r"\bno\.?\s*(\d+)\b",
            r"\boption\s+(\d+)\b",
            r"\bcase\s+(\d+)\b",
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                return int(match.group(1))

        return None

    @staticmethod
    def _describe_interpretation(
        interpretation: ConversationIntentResult,
    ) -> str:
        """Create a compact internal context record."""

        return (
            f"intent={interpretation.intent.value}; "
            f"mode={interpretation.mode.value}"
    )
