"""
Shadow Files application composition.

This module wires real business handlers into the controlled command
pipeline and establishes the persistent database required by the
application.
"""

from app.commands.models import CommandType
from app.commands.pipeline import CommandPipeline
from app.commands.service import CommandService
from app.investigation.research_service import (
    ResearchExecutionService,
)
from database.connection import initialize_database
from shadow_core.config import Config


def _database_path(database_url: str) -> str:
    """
    Convert the configured SQLite URL into a filesystem path.

    Shadow Files currently uses SQLite for persistent storage.
    """

    prefix = "sqlite:///"

    if not database_url.startswith(prefix):
        raise ValueError(
            "Shadow Files currently supports only SQLite "
            "database URLs."
        )

    path = database_url[len(prefix):]

    if not path:
        raise ValueError(
            "SQLite database path is required."
        )

    return path


def build_command_service() -> CommandService:
    """
    Build the configured Shadow Files command service.

    Database initialization happens here so every executable
    interface uses an initialized persistent database before
    business handlers are registered.
    """

    config = Config.from_env()

    database_path = _database_path(
        config.database_url
    )

    connection = initialize_database(
        database_path
    )

    # The connection is intentionally retained by the application
    # composition layer. Later persistence services will receive
    # this connection and use the same initialized database.
    connection.execute("SELECT 1")

    pipeline = CommandPipeline()

    research_service = ResearchExecutionService()

    pipeline.register_handler(
        CommandType.START_RESEARCH,
        research_service.execute,
    )

    return CommandService(
        pipeline=pipeline,
    )
