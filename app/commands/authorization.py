"""
Shadow Files command authorization layer.

Authorization is enforced before command execution.

A valid conversational intent does not grant permission to execute
a state-changing or operational command.
"""

from dataclasses import dataclass

from app.commands.models import Command, CommandType
from shadow_core.authorization import (
    Actor,
    AuthorizationError,
    require_role,
)


class CommandAuthorizationError(Exception):
    """Raised when a command is not authorized."""


@dataclass(frozen=True)
class CommandAuthorizationResult:
    """Result of command authorization."""

    authorized: bool
    command: Command
    reason: str = ""


READ_ONLY_COMMANDS = {
    CommandType.GET_STATUS,
    CommandType.GET_CASE_STATUS,
    CommandType.GET_SCHEDULE,
    CommandType.SHOW_HELP,
}

OPERATIONAL_COMMANDS = {
    CommandType.CONTINUE_CASE,
    CommandType.CHANGE_SCHEDULE,
    CommandType.START_RESEARCH,
    CommandType.ANALYZE_CASE,
}


class CommandAuthorizer:
    """Authorize commands according to the actor's role."""

    def authorize(
        self,
        actor: Actor,
        command: Command,
    ) -> CommandAuthorizationResult:
        """
        Check whether the actor may execute the command.

        Phase 10 uses the existing core role authorization boundary.
        No command bypasses authorization based on conversational intent.
        """

        if command.command_type in READ_ONLY_COMMANDS:
            return CommandAuthorizationResult(
                authorized=True,
                command=command,
            )

        if command.command_type in OPERATIONAL_COMMANDS:
            try:
                require_role(
                    actor,
                    "operator",
                )
            except AuthorizationError as exc:
                return CommandAuthorizationResult(
                    authorized=False,
                    command=command,
                    reason=str(exc),
                )

            return CommandAuthorizationResult(
                authorized=True,
                command=command,
            )

        raise CommandAuthorizationError(
            f"Unknown command authorization policy for "
            f"{command.command_type.value}."
)
