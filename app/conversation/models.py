"""
Shadow Files conversational models.

These models represent the conversation layer independently from
execution. Shadow can understand and retain conversational context
before deciding whether a user message should cause an action.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ConversationMode(str, Enum):
    """High-level mode of an incoming conversational turn."""

    CONVERSATION = "CONVERSATION"
    INFORMATION_REQUEST = "INFORMATION_REQUEST"
    EXECUTION_REQUEST = "EXECUTION_REQUEST"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"


class ConversationIntent(str, Enum):
    """Recognized conversational intents."""

    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    ASK_CAPABILITIES = "ASK_CAPABILITIES"
    FIND_CASES = "FIND_CASES"
    DISCUSS_CASE = "DISCUSS_CASE"
    SELECT_CASE = "SELECT_CASE"
    START_RESEARCH = "START_RESEARCH"
    CHECK_STATUS = "CHECK_STATUS"
    CONTINUE_WORK = "CONTINUE_WORK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ConversationMessage:
    """One normalized message in the conversation history."""

    role: str
    text: str


@dataclass
class ConversationContext:
    """
    State retained while Shadow is interacting with a user.

    The context deliberately stores conversational references separately
    from execution state. This allows phrases such as "number three",
    "that case", and "go ahead" to be resolved before execution.
    """

    turns: list[ConversationMessage] = field(default_factory=list)

    active_case_id: Optional[str] = None

    candidate_case_ids: list[str] = field(default_factory=list)

    def add_turn(self, role: str, text: str) -> None:
        """Add a message to the bounded conversation history."""

        self.turns.append(
            ConversationMessage(
                role=role,
                text=text,
            )
        )

        # Keep enough recent context for natural conversation without
        # allowing the in-memory context to grow without limit.
        if len(self.turns) > 50:
            del self.turns[:-50]

    def set_active_case(self, case_id: str) -> None:
        """Set the case currently being discussed or worked on."""

        if not case_id:
            raise ValueError("case_id is required.")

        self.active_case_id = case_id

    def set_candidate_cases(self, case_ids: list[str]) -> None:
        """Store the ordered candidate cases returned by discovery."""

        self.candidate_case_ids = list(case_ids)

    def select_candidate(self, index: int) -> str:
        """
        Select a candidate by its one-based conversational number.

        Example:
            "Let's use number three."
        """

        if index < 1 or index > len(self.candidate_case_ids):
            raise IndexError("Candidate case number is out of range.")

        case_id = self.candidate_case_ids[index - 1]
        self.active_case_id = case_id
        return case_id


@dataclass(frozen=True)
class ConversationIntentResult:
    """
    Result of interpreting one conversational turn.

    This object describes what the user appears to mean. It does not
    itself execute anything.
    """

    mode: ConversationMode
    intent: ConversationIntent
    confidence: float = 1.0
    target: Optional[str] = None
    parameters: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0."
  )
