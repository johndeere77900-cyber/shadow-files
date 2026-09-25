"""
Shadow Files conversational interpreter.

The interpreter converts ordinary human language into a structured
conversation intent.

It does not execute commands, perform research, publish content, or
change application state. Execution remains the responsibility of the
command/application layers.
"""

import re

from app.conversation.models import (
    ConversationIntent,
    ConversationIntentResult,
    ConversationMode,
)


class ConversationInterpreter:
    """
    Interpret common conversational requests.

    This is intentionally deterministic at the foundation layer.
    A future language-model provider can sit behind this interface
    without allowing the model to bypass execution controls.
    """

    def interpret(
        self,
        text: str,
    ) -> ConversationIntentResult:
        """Interpret one user message."""

        if not text or not text.strip():
            return ConversationIntentResult(
                mode=ConversationMode.CLARIFICATION_REQUIRED,
                intent=ConversationIntent.UNKNOWN,
                confidence=1.0,
            )

        normalized = text.strip().lower()

        if self._is_capability_question(normalized):
            return ConversationIntentResult(
                mode=ConversationMode.INFORMATION_REQUEST,
                intent=ConversationIntent.ASK_CAPABILITIES,
            )

        if self._is_find_cases_request(normalized):
            return ConversationIntentResult(
                mode=ConversationMode.EXECUTION_REQUEST,
                intent=ConversationIntent.FIND_CASES,
            )

        if self._is_research_request(normalized):
            return ConversationIntentResult(
                mode=ConversationMode.EXECUTION_REQUEST,
                intent=ConversationIntent.START_RESEARCH,
            )

        if self._is_status_request(normalized):
            return ConversationIntentResult(
                mode=ConversationMode.INFORMATION_REQUEST,
                intent=ConversationIntent.CHECK_STATUS,
            )

        if self._is_continue_request(normalized):
            return ConversationIntentResult(
                mode=ConversationMode.EXECUTION_REQUEST,
                intent=ConversationIntent.CONTINUE_WORK,
            )

        candidate_number = self._candidate_number(normalized)

        if candidate_number is not None:
            return ConversationIntentResult(
                mode=ConversationMode.CONVERSATION,
                intent=ConversationIntent.SELECT_CASE,
                target=str(candidate_number),
            )

        if self._is_discussion(normalized):
            return ConversationIntentResult(
                mode=ConversationMode.CONVERSATION,
                intent=ConversationIntent.DISCUSS_CASE,
            )

        return ConversationIntentResult(
            mode=ConversationMode.CONVERSATION,
            intent=ConversationIntent.GENERAL_CONVERSATION,
        )

    @staticmethod
    def _is_capability_question(text: str) -> bool:
        patterns = (
            "what can you do",
            "what do you do",
            "what are you capable of",
            "what can shadow do",
            "how can you help",
        )
        return any(pattern in text for pattern in patterns)

    @staticmethod
    def _is_find_cases_request(text: str) -> bool:
        patterns = (
            "find me",
            "find some",
            "find cases",
            "find stories",
            "look for cases",
            "look for stories",
            "give me cases",
            "give me stories",
            "search for cases",
            "search for stories",
        )

        crime_terms = (
            "true crime",
            "crime",
            "case",
            "cases",
            "story",
            "stories",
            "mystery",
            "mysteries",
            "cold case",
            "cold cases",
            "disappearance",
            "disappearances",
        )

        return (
            any(pattern in text for pattern in patterns)
            and any(term in text for term in crime_terms)
        )

    @staticmethod
    def _is_research_request(text: str) -> bool:
        patterns = (
            "research this",
            "research it",
            "research the case",
            "start researching",
            "go ahead and research",
            "investigate this",
            "investigate it",
            "start the investigation",
        )
        return any(pattern in text for pattern in patterns)

    @staticmethod
    def _is_status_request(text: str) -> bool:
        patterns = (
            "what is the status",
            "what's the status",
            "check the status",
            "how are we doing",
            "where are we",
            "what have we done",
            "show status",
        )
        return any(pattern in text for pattern in patterns)

    @staticmethod
    def _is_continue_request(text: str) -> bool:
        patterns = (
            "go ahead",
            "continue",
            "continue working",
            "keep going",
            "start working on it",
            "proceed with it",
            "proceed",
        )
        return any(pattern in text for pattern in patterns)

    @staticmethod
    def _candidate_number(text: str) -> int | None:
        patterns = (
            r"\bnumber\s+(\d+)\b",
            r"\bno\.?\s*(\d+)\b",
            r"\boption\s+(\d+)\b",
            r"\bcase\s+(\d+)\b",
        )

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))

        return None

    @staticmethod
    def _is_discussion(text: str) -> bool:
        patterns = (
            "what do you think",
            "tell me about this case",
            "talk about this case",
            "could we make a story",
            "would this work",
            "is this suitable",
            "what kind of cases",
            "discuss this",
        )
        return any(pattern in text for pattern in patterns)
