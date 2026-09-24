"""
Shadow Files command models.

Commands are the controlled execution representation produced after
conversation parsing and validation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CommandType(str, Enum):
    """Recognized executable command categories."""

    GET_STATUS = "GET_STATUS"
    GET_CASE_STATUS = "GET_CASE_STATUS"
    CONTINUE_CASE = "CONTINUE_CASE"
    CHANGE_SCHEDULE = "CHANGE_SCHEDULE"
    START_RESEARCH = "START_RESEARCH"
    ANALYZE_CASE = "ANALYZE_CASE"
    GET_SCHEDULE = "GET_SCHEDULE"
    SHOW_HELP = "SHOW_HELP"


@dataclass(frozen=True)
class Command:
    """A validated command ready for controlled dispatch."""

    command_type: CommandType
    source_intent: str
    target: Optional[str] = None
    parameters: tuple[tuple[str, str], ...] = ()
