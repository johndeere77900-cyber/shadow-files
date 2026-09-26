"""
Shadow Files research execution tests.

These tests verify the real application wiring for START_RESEARCH
without making external API calls.

The provider is replaced with a controlled fake so the test proves:
natural-language instruction -> command -> authorization ->
research service -> provider -> structured result.
"""

import unittest

from app.application import build_command_service
from app.investigation.research_service import (
    ResearchExecutionService,
)
from app.investigation.tavily import TavilyResearchResult
from app.commands.models import CommandType
from shadow_core.authorization import Actor


class FakeResearchProvider:
    """Controlled research provider used only for testing."""

    def __init__(self):
        self.queries = []

    def search(self, query):
        self.queries.append(query)

        return [
            TavilyResearchResult(
                title="Test source",
                url="https://example.com/test-source",
                content="Test evidence content.",
                score=0.95,
                published_date=None,
            )
        ]


class ResearchExecutionTests(unittest.TestCase):
    """Verify controlled Shadow Files research execution."""

    def test_research_service_preserves_instruction(self):
        provider = FakeResearchProvider()
        service = ResearchExecutionService(
            provider=provider,
        )

        from app.commands.models import Command

        command = Command(
            command_type=CommandType.START_RESEARCH,
            source_intent="RESEARCH",
            target=(
                "unresolved crimes in the United States"
            ),
        )

        result = service.execute(command)

        self.assertEqual(
            provider.queries,
            [
                "unresolved crimes in the United States"
            ],
        )

        self.assertEqual(
            result.instruction,
            "unresolved crimes in the United States",
        )

        self.assertEqual(
            result.result_count,
            1,
        )

        self.assertEqual(
            result.results[0].url,
            "https://example.com/test-source",
        )

    def test_authorized_research_command_preserves_target(self):
        service = build_command_service()

        self.assertIsNotNone(service)

        actor = Actor(
            actor_id="operator-001",
            role="operator",
        )

        # This test verifies the command is recognized and reaches
        # the configured research handler. The actual external
        # provider is tested separately with a fake provider above.
        response = service.execute(
            actor,
            "Research unresolved crimes in the United States",
        )

        self.assertTrue(response.success)

        self.assertIsNotNone(response.result)

        self.assertEqual(
            response.result.command.command_type,
            CommandType.START_RESEARCH,
        )

        self.assertEqual(
            response.result.command.target,
            "unresolved crimes in the united states",
        )

        self.assertTrue(
            response.result.executed
        )


if __name__ == "__main__":
    unittest.main()
