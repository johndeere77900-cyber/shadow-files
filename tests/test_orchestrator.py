"""
Shadow Files orchestration-layer tests.

Phase 10 verifies that user text can move through the controlled
pipeline without bypassing validation or execution boundaries.
"""

import unittest

from app.commands.dispatcher import CommandDispatcher
from app.commands.models import CommandType
from app.commands.orchestrator import (
    CommandOrchestrator,
    OrchestrationError,
)


class CommandOrchestratorTests(unittest.TestCase):
    """Test controlled command orchestration."""

    def test_prepare_does_not_execute_handler(self):
        dispatcher = CommandDispatcher()
        executions = []

        def handler(command):
            executions.append(command)
            return "executed"

        orchestrator = CommandOrchestrator(
            dispatcher=dispatcher,
        )

        orchestrator.register_handler(
            CommandType.GET_STATUS,
            handler,
        )

        intent, command, validation = orchestrator.prepare(
            "How are we doing?"
        )

        self.assertEqual(
            command.command_type,
            CommandType.GET_STATUS,
        )
        self.assertTrue(validation.valid)
        self.assertEqual(
            intent.intent_type.value,
            "STATUS",
        )
        self.assertEqual(
            executions,
            [],
        )

    def test_execute_runs_registered_handler(self):
        dispatcher = CommandDispatcher()

        def handler(command):
            return "status-ok"

        orchestrator = CommandOrchestrator(
            dispatcher=dispatcher,
        )

        orchestrator.register_handler(
            CommandType.GET_STATUS,
            handler,
        )

        result = orchestrator.execute(
            "How are we doing?"
        )

        self.assertTrue(result.executed)
        self.assertIsNotNone(result.dispatch)
        self.assertTrue(result.dispatch.success)
        self.assertEqual(
            result.dispatch.data,
            "status-ok",
        )

    def test_unknown_request_cannot_execute(self):
        dispatcher = CommandDispatcher()
        executions = []

        def handler(command):
            executions.append(command)

        orchestrator = CommandOrchestrator(
            dispatcher=dispatcher,
        )

        orchestrator.register_handler(
            CommandType.GET_STATUS,
            handler,
        )

        with self.assertRaises(OrchestrationError):
            orchestrator.execute(
                "Do something completely unknown."
            )

        self.assertEqual(
            executions,
            [],
        )

    def test_research_command_requires_registered_handler(self):
        orchestrator = CommandOrchestrator()

        with self.assertRaises(Exception):
            orchestrator.execute(
                "Research this case."
            )

    def test_dispatch_failure_is_returned_without_being_hidden(self):
        dispatcher = CommandDispatcher()

        def handler(command):
            raise RuntimeError(
                "research provider unavailable"
            )

        orchestrator = CommandOrchestrator(
            dispatcher=dispatcher,
        )

        orchestrator.register_handler(
            CommandType.START_RESEARCH,
            handler,
        )

        result = orchestrator.execute(
            "Research this case."
        )

        self.assertFalse(result.executed)
        self.assertIsNotNone(result.dispatch)
        self.assertFalse(result.dispatch.success)
        self.assertEqual(
            result.dispatch.error,
            "research provider unavailable",
        )


if __name__ == "__main__":
    unittest.main()
