"""
Shadow Files command validation.

A mapped command must pass this boundary before it can reach an
execution dispatcher.
"""

from dataclasses import dataclass

from app.commands.models import Command


@dataclass(frozen=True)
class CommandValidationResult:
    """Result of command validation."""

    valid: bool
    command: Command
    reason: str = ""


class CommandValidator:
    """Validate commands before execution."""

    def validate(
        self,
        command: Command,
    ) -> CommandValidationResult:
        """Validate a command without executing it."""

        if not command.source_intent:
            return CommandValidationResult(
                valid=False,
                command=command,
                reason="Command source intent is required.",
            )

        if not command.command_type:
            return CommandValidationResult(
                valid=False,
                command=command,
                reason="Command type is required.",
            )

        if not isinstance(
            command.parameters,
            tuple,
        ):
            return CommandValidationResult(
                valid=False,
                command=command,
                reason="Command parameters must be a tuple.",
            )

        return CommandValidationResult(
            valid=True,
            command=command,
          )
