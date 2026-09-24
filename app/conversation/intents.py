"""
Shadow Files intent models.

An intent is the structured representation of what the user is asking
Shadow Files to understand or eventually execute.

Intent creation does not execute any operation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class IntentType(str, Enum):
    """Recognized Shadow Files conversational intents."""

    STATUS = "STATUS"
    CASE_STATUS = "CASE_STATUS"
    CONTINUE_CASE = "CONTINUE_CASE"
    SCHEDULE_CHANGE = "SCHEDULE_CHANGE"
    RESEARCH = "RESEARCH"
    ANALYZE = "ANALYZE"
    SHOW_SCHEDULE = "SHOW_SCHEDULE"
    HELP = "HELP"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Intent:
    """Structured interpretation of a user request."""

    intent_type: IntentType
    raw_text: str
    target: Optional[str] = None
    parameters: tuple[tuple[str, str], ...] = ()
    confidence: float = 1.0
