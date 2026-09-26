"""
Shadow Files research execution service.

This service connects the controlled command layer to the real
research provider and prepares the returned sources for investigation
persistence.

Research results remain unverified. This service does not:
- declare claims to be facts,
- verify allegations,
- create production content,
- publish content,
- bypass authorization,
- or silently invent case identity.
"""

from dataclasses import dataclass
from typing import Any

from app.commands.models import Command, CommandType
from app.investigation.tavily import (
    TavilyResearchProvider,
    TavilyResearchResult,
)


class ResearchExecutionError(Exception):
    """Raised when a Shadow Files research operation fails."""


@dataclass(frozen=True)
class ResearchExecutionResult:
    """Structured result of one Shadow Files research operation."""

    instruction: str
    results: tuple[TavilyResearchResult, ...]
    case_id: str | None = None

    @property
    def result_count(self) -> int:
        """Return the number of sources returned."""
        return len(self.results)

    @property
    def has_case_context(self) -> bool:
        """Return whether the research has an explicit case context."""
        return bool(self.case_id)


class ResearchExecutionService:
    """
    Execute controlled research commands through the configured
    research provider.

    Case identity is taken from the command parameters when supplied.
    It is never inferred or invented from the research text.
    """

    def __init__(
        self,
        provider: TavilyResearchProvider | None = None,
    ) -> None:
        self._provider = (
            provider or TavilyResearchProvider()
        )

    def execute(
        self,
        command: Command,
    ) -> ResearchExecutionResult:
        """
        Execute a validated START_RESEARCH command.

        The command must contain a non-empty research target.

        An optional case_id may be supplied through command parameters.
        The service preserves that context for the next persistence
        stage but never invents a case identity.
        """

        if command.command_type != CommandType.START_RESEARCH:
            raise ResearchExecutionError(
                "ResearchExecutionService can only execute "
                "START_RESEARCH commands."
            )

        instruction = (
            command.target.strip()
            if command.target
            else ""
        )

        if not instruction:
            raise ResearchExecutionError(
                "Research instruction is required."
            )

        case_id = self._get_case_id(
            command.parameters
        )

        try:
            results = self._provider.search(
                instruction
            )
        except Exception as exc:
            raise ResearchExecutionError(
                str(exc)
            ) from exc

        return ResearchExecutionResult(
            instruction=instruction,
            results=tuple(results),
            case_id=case_id,
        )

    @staticmethod
    def _get_case_id(
        parameters: tuple[tuple[str, str], ...],
    ) -> str | None:
        """Extract an explicit case_id without inventing one."""

        for key, value in parameters:
            if key == "case_id":
                normalized = value.strip()

                if normalized:
                    return normalized

        return None
