"""
Shadow Files command dispatcher.

The dispatcher is the controlled boundary between a validated command
and an executable operation.

Actual business operations will be connected in later phases.
"""

from dataclasses import dataclass
from typing import Any, Callable

from app.commands.models import (
    Command,
    CommandType,
)


class CommandDispatchError(Exception):
    """Raised when a command cannot be dispatched."""


@dataclass(frozen=True)
class CommandResult:
    """Result returned by a dispatched command."""

    command: Command
    success: bool
    data: Any = None
    error: str = ""


class CommandDispatcher:
    """Dispatch commands to explicitly registered handlers."""

    def __init__(self) -> None:
        self._handlers: dict[
            CommandType,
            Callable[[Command], Any],
        ] = {}

    def register(
        self,
        command_type: CommandType,
        handler: Callable[[Command], Any],
    ) -> None:
        """Register a handler for a specific command type."""

        if not callable(handler):
            raise CommandDispatchError(
                "Command handler must be callable."
            )

        self._handlers[command_type] = handler

    def dispatch(
        self,
        command: Command,
    ) -> CommandResult:
        """Dispatch a command to its registered handler."""

        handler = self._handlers.get(
            command.command_type
        )

        if handler is None:
            raise CommandDispatchError(
                f"No handler registered for command "
                f"{command.command_type.value}."
            )

        try:
            data = handler(command)

            return CommandResult(
                command=command,
                success=True,
                data=data,
            )

        except Exception as exc:
            return CommandResult(
                command=command,
                success=False,
                error=str(exc),
          )
