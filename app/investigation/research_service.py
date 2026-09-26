"""
Shadow Files research execution service.

This service connects the controlled command layer to the real
research provider.

The service performs research only. It does not:
- verify claims,
- declare allegations to be facts,
- create production content,
- publish content,
- bypass authorization,
- or replace the evidence-review process.

Those responsibilities remain separate.
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

    @property
    def result_count(self) -> int:
        """Return the number of sources returned."""
        return len(self.results)


class ResearchExecutionService:
    """
    Execute controlled research commands through the configured
    research provider.
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
          )
