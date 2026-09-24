"""
Shadow Files command service.

Provides the application-facing entry point for command execution.

The service keeps the Telegram/interface layer independent from the
internal command pipeline.
"""

from dataclasses import dataclass

from app.commands.pipeline import (
    CommandPipeline,
    PipelineResult,
)
from shadow_core.authorization import Actor


@dataclass(frozen=True)
class CommandServiceResponse:
    """Safe application response from command execution."""

    success: bool
    message: str
    result: PipelineResult | None = None


class CommandService:
    """Application service for controlled Shadow Files commands."""

    def __init__(
        self,
        pipeline: CommandPipeline | None = None,
    ) -> None:
        self._pipeline = (
            pipeline or CommandPipeline()
        )

    def execute(
        self,
        actor: Actor,
        text: str,
    ) -> CommandServiceResponse:
        """Execute a user command through the controlled pipeline."""

        try:
            result = self._pipeline.execute(
                actor,
                text,
            )

        except Exception as exc:
            return CommandServiceResponse(
                success=False,
                message=str(exc),
            )

        if not result.authorization.authorized:
            return CommandServiceResponse(
                success=False,
                message=(
                    "You are not authorized to execute "
                    "this command."
                ),
                result=result,
            )

        if result.dispatch is None:
            return CommandServiceResponse(
                success=False,
                message="Command was not executed.",
                result=result,
            )

        if not result.dispatch.success:
            return CommandServiceResponse(
                success=False,
                message=result.dispatch.error,
                result=result,
            )

        return CommandServiceResponse(
            success=True,
            message="Command executed successfully.",
            result=result,
        )

    def register_handler(
        self,
        command_type,
        handler,
    ) -> None:
        """Expose controlled handler registration to the application."""

        self._pipeline.register_handler(
            command_type,
            handler,
          )
