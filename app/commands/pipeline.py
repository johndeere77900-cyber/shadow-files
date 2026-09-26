"""
Shadow Files controlled command pipeline.

This module provides the complete Phase 10 safety boundary:

incoming text
    -> conversation parsing
    -> intent validation
    -> command mapping
    -> command validation
    -> authorization
    -> dispatch

No step may be skipped.
"""

from dataclasses import dataclass

from app.commands.authorization import (
    CommandAuthorizationResult,
    CommandAuthorizer,
)
from app.commands.dispatcher import (
    CommandDispatcher,
    CommandResult,
)
from app.commands.models import Command
from app.commands.orchestrator import (
    CommandOrchestrator,
)
from app.commands.validation import (
    CommandValidationResult,
)
from app.conversation.intents import Intent
from shadow_core.authorization import Actor


class CommandPipelineError(Exception):
    """Raised when the command pipeline cannot proceed."""


@dataclass(frozen=True)
class PipelineResult:
    """Complete result of a controlled command pipeline."""

    intent: Intent
    command: Command
    validation: CommandValidationResult
    authorization: CommandAuthorizationResult
    dispatch: CommandResult | None
    executed: bool


class CommandPipeline:
    """Execute commands through every Phase 10 safety boundary."""

    def __init__(
        self,
        orchestrator: CommandOrchestrator | None = None,
        authorizer: CommandAuthorizer | None = None,
        dispatcher: CommandDispatcher | None = None,
    ) -> None:
        self._dispatcher = (
            dispatcher or CommandDispatcher()
        )

        self._orchestrator = (
            orchestrator
            or CommandOrchestrator(
                dispatcher=self._dispatcher,
            )
        )

        self._authorizer = (
            authorizer or CommandAuthorizer()
        )

    def register_handler(
        self,
        command_type,
        handler,
    ) -> None:
        """Register an explicit executable command handler."""

        self._dispatcher.register(
            command_type,
            handler,
        )

    def execute(
        self,
        actor: Actor,
        text: str,
    ) -> PipelineResult:
        """
        Process and execute a command through all safety boundaries.
        """

        try:
            (
                intent,
                command,
                validation,
            ) = self._orchestrator.prepare(text)

        except Exception as exc:
            raise CommandPipelineError(
                str(exc)
            ) from exc

        authorization = self._authorizer.authorize(
            actor,
            command,
        )

        if not authorization.authorized:
            return PipelineResult(
                intent=intent,
                command=command,
                validation=validation,
                authorization=authorization,
                dispatch=None,
                executed=False,
            )

        dispatch = self._dispatcher.dispatch(
            command
        )

        return PipelineResult(
            intent=intent,
            command=command,
            validation=validation,
            authorization=authorization,
            dispatch=dispatch,
            executed=dispatch.success,
        )
