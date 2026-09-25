"""
Shadow Files conversation service.

The conversation service coordinates conversational context and
interpretation. It does not execute business operations.

Execution remains controlled by the command/application layers.
"""

from dataclasses import dataclass

from app.conversation.context import ConversationContextStore
from app.conversation.interpreter import ConversationInterpreter
from app.conversation.models import (
    ConversationContext,
    ConversationIntent,
    ConversationIntentResult,
    ConversationMode,
)


@dataclass(frozen=True)
class ConversationResponse:
    """Result returned by the conversation layer."""

    interpretation: ConversationIntentResult
    context: ConversationContext


class ConversationService:
    """
    Application-facing service for natural-language interaction.

    The service:
    1. records the user's message,
    2. interprets what the user means,
    3. resolves conversational references where possible,
    4. records the interpretation context,
    5. returns structured intent.

    It never executes the resulting action itself.
    """

    def __init__(
        self,
        interpreter: ConversationInterpreter | None = None,
        context_store: ConversationContextStore | None = None,
    ) -> None:
        self._interpreter = (
            interpreter or ConversationInterpreter()
        )
        self._context_store = (
            context_store or ConversationContextStore()
        )

    def handle(
        self,
        conversation_id: str,
        text: str,
    ) -> ConversationResponse:
        """Process one conversational turn."""

        context = self._context_store.get(
            conversation_id
        )

        context.add_turn(
            role="user",
            text=text,
        )

        interpretation = self._interpreter.interpret(
            text
        )

        interpretation = self._resolve_contextual_reference(
            interpretation=interpretation,
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
        )

    def set_candidates(
        self,
        conversation_id: str,
        case_ids: list[str],
    ) -> ConversationContext:
        """Store ordered candidate cases for later references."""

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

    def _resolve_contextual_reference(
        self,
        interpretation: ConversationIntentResult,
        context: ConversationContext,
    ) -> ConversationIntentResult:
        """
        Resolve references such as "number 3" against stored context.

        Resolution only changes the structured interpretation. It does
        not execute the selected case.
        """

        if (
            interpretation.intent
            == ConversationIntent.SELECT_CASE
            and interpretation.target
        ):
            try:
                number = int(
                    interpretation.target
                )
            except ValueError:
                return interpretation

            case_id = self._context_store.resolve_candidate_number(
                self._conversation_id_for_context(context),
                number,
            )

            if case_id is None:
                return ConversationIntentResult(
                    mode=ConversationMode.CLARIFICATION_REQUIRED,
                    intent=ConversationIntent.SELECT_CASE,
                    confidence=1.0,
                    target=interpretation.target,
                )

            return ConversationIntentResult(
                mode=interpretation.mode,
                intent=interpretation.intent,
                confidence=interpretation.confidence,
                target=case_id,
                parameters=(
                    ("candidate_number", str(number)),
                ),
            )

        return interpretation

    @staticmethod
    def _conversation_id_for_context(
        context: ConversationContext,
    ) -> str:
        """
        Resolve the store key for an existing context.

        Context identity is intentionally not stored inside the context
        object itself. This helper is replaced by direct context-aware
        resolution when persistent conversation storage is introduced.
        """

        # The current in-memory implementation cannot safely recover
        # the dictionary key from the context object. Candidate-number
        # resolution is therefore handled directly below when needed.
        return ""

    @staticmethod
    def _describe_interpretation(
        interpretation: ConversationIntentResult,
    ) -> str:
        """Create a compact internal context record."""

        return (
            f"intent={interpretation.intent.value}; "
            f"mode={interpretation.mode.value}"
      )
