"""
Shadow Files command orchestration layer.

The orchestrator connects conversation handling, command mapping,
command validation, and controlled dispatch.

It does not contain business logic for research, production,
scheduling, or publishing.
"""

from dataclasses import dataclass

from app.commands.dispatcher import (
    CommandDispatcher,
    CommandResult,
)
from app.commands.mapping import (
    CommandMappingError,
    map_intent_to_command,
)
from app.commands.models import Command
from app.commands.validation import (
    CommandValidationResult,
    CommandValidator,
)
from app.conversation.handler import (
    ConversationHandler,
)
from app.conversation.intents import Intent


class OrchestrationError(Exception):
    """Raised when command orchestration cannot proceed."""


@dataclass(frozen=True)
class OrchestrationResult:
    """Complete result of an orchestration attempt."""

    intent: Intent
    command: Command | None
    validation: CommandValidationResult | None
    dispatch: CommandResult | None
    executed: bool


class CommandOrchestrator:
    """
    Controlled pipeline from user text to command execution.

    The execution boundary is the dispatcher. No command is executed
    unless conversation parsing, intent validation, command mapping,
    and command validation all succeed.
    """

    def __init__(
        self,
        conversation_handler: ConversationHandler | None = None,
        command_validator: CommandValidator | None = None,
        dispatcher: CommandDispatcher | None = None,
    ) -> None:
        self._conversation_handler = (
            conversation_handler or ConversationHandler()
        )
        self._command_validator = (
            command_validator or CommandValidator()
        )
        self._dispatcher = (
            dispatcher or CommandDispatcher()
        )

    def register_handler(
        self,
        command_type,
        handler,
    ) -> None:
        """Register an explicit handler with the dispatcher."""

        self._dispatcher.register(
            command_type,
            handler,
        )

    def prepare(
        self,
        text: str,
    ) -> tuple[Intent, Command, CommandValidationResult]:
        """
        Parse, validate, map, and validate a command without executing it.
        """

        conversation_result = (
            self._conversation_handler.handle(text)
        )

        if not conversation_result.validation.valid:
            raise OrchestrationError(
                conversation_result.validation.reason
            )

        intent = conversation_result.intent

        try:
            command = map_intent_to_command(intent)
        except CommandMappingError as exc:
            raise OrchestrationError(
                str(exc)
            ) from exc

        validation = self._command_validator.validate(
            command
        )

        if not validation.valid:
            raise OrchestrationError(
                validation.reason
            )

        return (
            intent,
            command,
            validation,
        )

    def execute(
        self,
        text: str,
    ) -> OrchestrationResult:
        """
        Execute a command only after all validation boundaries pass.

        The executed flag represents successful dispatch execution.
        A dispatch attempt that returns success=False is therefore not
        reported as executed.
        """

        intent, command, validation = self.prepare(text)

        dispatch_result = self._dispatcher.dispatch(
            command
        )

        return OrchestrationResult(
            intent=intent,
            command=command,
            validation=validation,
            dispatch=dispatch_result,
            executed=dispatch_result.success,
    )
