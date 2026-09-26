"""
Shadow Files application composition.

This module wires the real business handlers into the controlled
command pipeline and connects research execution to persistent
investigation storage when an explicit case_id is supplied.
"""

import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.commands.models import Command, CommandType
from app.commands.pipeline import CommandPipeline
from app.commands.service import CommandService
from app.cases.repository import CaseRepository
from app.investigation.models import ResearchStatus
from app.investigation.repository import InvestigationRepository
from app.investigation.research_service import (
    ResearchExecutionResult,
    ResearchExecutionService,
)
from app.investigation.service import InvestigationService
from app.investigation.sources import create_research_source
from database.connection import initialize_database
from shadow_core.config import Config


def _database_path(database_url: str) -> str:
    """
    Convert the configured SQLite URL into a filesystem path.
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


def _source_publisher(url: str) -> str | None:
    """
    Extract a simple publisher/domain from a source URL.
    """

    hostname = urlparse(url).hostname

    if not hostname:
        return None

    return hostname


def _persist_research(
    command: Command,
    result: ResearchExecutionResult,
    case_repository: CaseRepository,
    investigation_service: InvestigationService,
    investigation_repository: InvestigationRepository,
) -> ResearchExecutionResult:
    """
    Persist research results when an explicit case_id is supplied.

    Case identity is never inferred from the research instruction.
    """

    case_id = result.case_id

    if not case_id:
        return result

    case = case_repository.get(case_id)

    if case is None:
        raise ValueError(
            f"Case '{case_id}' does not exist."
        )

    investigation_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)

    investigation_service.create(
        investigation_id=investigation_id,
        case_id=case.case_id,
        started_at=started_at,
        notes=(
            "Shadow Files research investigation for: "
            f"{result.instruction}"
        ),
    )

    investigation_service.change_status(
        investigation_id,
        ResearchStatus.RESEARCHING,
    )

    for research_result in result.results:
        source_id = str(uuid.uuid4())

        source = create_research_source(
            source_id=source_id,
            investigation_id=investigation_id,
            name=(
                research_result.title
                or research_result.url
            ),
            url=research_result.url,
            publisher=_source_publisher(
                research_result.url
            ),
            discovered_at=started_at,
        )

        investigation_repository.create_source(
            source
        )

    investigation_service.change_status(
        investigation_id,
        ResearchStatus.EVIDENCE_REVIEW,
    )

    return result


def build_command_service() -> CommandService:
    """
    Build the configured Shadow Files command service.

    The database is initialized once and the same connection is
    supplied to the persistence components used by research.
    """

    config = Config.from_env()

    database_path = _database_path(
        config.database_url
    )

    connection = initialize_database(
        database_path
    )

    case_repository = CaseRepository(
        connection
    )

    investigation_service = InvestigationService(
        connection
    )

    investigation_repository = InvestigationRepository(
        connection
    )

    research_service = ResearchExecutionService()

    def execute_research(
        command: Command,
    ) -> ResearchExecutionResult:
        result = research_service.execute(
            command
        )

        return _persist_research(
            command=command,
            result=result,
            case_repository=case_repository,
            investigation_service=investigation_service,
            investigation_repository=investigation_repository,
        )

    pipeline = CommandPipeline()

    pipeline.register_handler(
        CommandType.START_RESEARCH,
        execute_research,
    )

    return CommandService(
        pipeline=pipeline,
    )
