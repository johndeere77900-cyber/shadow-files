"""
Shadow Files intent-to-command mapping.

This module converts validated conversational intents into controlled
command types.

It does not execute commands.
"""

from app.commands.models import (
    Command,
    CommandType,
)
from app.conversation.intents import (
    Intent,
    IntentType,
)


class CommandMappingError(Exception):
    """Raised when an intent cannot be mapped to a command."""


INTENT_TO_COMMAND = {
    IntentType.STATUS: CommandType.GET_STATUS,
    IntentType.CASE_STATUS: CommandType.GET_CASE_STATUS,
    IntentType.CONTINUE_CASE: CommandType.CONTINUE_CASE,
    IntentType.SCHEDULE_CHANGE: CommandType.CHANGE_SCHEDULE,
    IntentType.RESEARCH: CommandType.START_RESEARCH,
    IntentType.ANALYZE: CommandType.ANALYZE_CASE,
    IntentType.SHOW_SCHEDULE: CommandType.GET_SCHEDULE,
    IntentType.HELP: CommandType.SHOW_HELP,
}


def map_intent_to_command(
    intent: Intent,
) -> Command:
    """
    Convert a recognized intent into a command.

    Unknown intents are never converted into executable commands.
    """

    command_type = INTENT_TO_COMMAND.get(
        intent.intent_type
    )

    if command_type is None:
        raise CommandMappingError(
            f"No command mapping exists for intent "
            f"{intent.intent_type.value}."
        )

    return Command(
        command_type=command_type,
        source_intent=intent.intent_type.value,
        target=intent.target,
        parameters=intent.parameters,
  )
