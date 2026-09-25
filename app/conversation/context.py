"""
Shadow Files conversation context management.

This module owns conversational context independently from command
execution. It allows Shadow to understand references to earlier parts
of the conversation without executing actions by itself.
"""

from dataclasses import dataclass
from typing import Optional

from app.conversation.models import ConversationContext


@dataclass
class ConversationContextStore:
    """
    In-memory conversation context store.

    A separate context is maintained for each authorized conversation.
    """

    contexts: dict[str, ConversationContext]

    def __init__(self) -> None:
        self.contexts = {}

    def get(self, conversation_id: str) -> ConversationContext:
        """Return the context for a conversation, creating it if needed."""

        if not conversation_id:
            raise ValueError("conversation_id is required.")

        if conversation_id not in self.contexts:
            self.contexts[conversation_id] = ConversationContext()

        return self.contexts[conversation_id]

    def clear(self, conversation_id: str) -> None:
        """Clear the context for one conversation."""

        self.contexts.pop(conversation_id, None)

    def set_active_case(
        self,
        conversation_id: str,
        case_id: str,
    ) -> ConversationContext:
        """Set the active case for a conversation."""

        context = self.get(conversation_id)
        context.set_active_case(case_id)
        return context

    def set_candidate_cases(
        self,
        conversation_id: str,
        case_ids: list[str],
    ) -> ConversationContext:
        """Store the ordered candidate cases for a conversation."""

        context = self.get(conversation_id)
        context.set_candidate_cases(case_ids)
        return context

    def resolve_candidate_number(
        self,
        conversation_id: str,
        number: int,
    ) -> Optional[str]:
        """
        Resolve a one-based candidate number.

        This supports natural references such as "number 3" without
        directly executing any case operation.
        """

        context = self.get(conversation_id)

        try:
            return context.select_candidate(number)
        except IndexError:
            return None
