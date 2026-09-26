"""
Shadow Files application composition.

This module wires real business handlers into the controlled command
pipeline.

Interfaces such as CLI and Telegram should obtain their CommandService
from this module so they share the same execution path.
"""

from app.commands.models import CommandType
from app.commands.pipeline import CommandPipeline
from app.commands.service import CommandService
from app.investigation.research_service import (
    ResearchExecutionService,
)


def build_command_service() -> CommandService:
    """
    Build the configured Shadow Files command service.

    All executable business handlers are registered here rather than
    inside interface or transport modules.
    """

    pipeline = CommandPipeline()

    research_service = ResearchExecutionService()

    pipeline.register_handler(
        CommandType.START_RESEARCH,
        research_service.execute,
    )

    return CommandService(
        pipeline=pipeline,
    )
