"""
Shadow Files command-pipeline tests.

Phase 10 verifies the complete controlled path from user text through
validation, authorization, and dispatch.
"""

import unittest

from app.commands.models import CommandType
from app.commands.pipeline import (
    CommandPipeline,
)
from shadow_core.authorization import Actor


class CommandPipelineTests(unittest.TestCase):
    """Test the complete Phase 10 command pipeline."""

    def setUp(self):
        self.operator = Actor(
            actor_id="operator-001",
            role="operator",
        )

        self.viewer = Actor(
            actor_id="viewer-001",
            role="viewer",
        )

        self.pipeline = CommandPipeline()

    def test_read_command_reaches_handler(self):
        self.pipeline.register_handler(
            CommandType.GET_STATUS,
            lambda command: "system-ok",
        )

        result = self.pipeline.execute(
            self.viewer,
            "How are we doing?",
        )

        self.assertTrue(result.validation.valid)
        self.assertTrue(result.authorization.authorized)
        self.assertTrue(result.executed)
        self.assertIsNotNone(result.dispatch)
        self.assertTrue(result.dispatch.success)
        self.assertEqual(
            result.dispatch.data,
            "system-ok",
        )

    def test_unauthorized_command_does_not_execute(self):
        executions = []

        def handler(command):
            executions.append(command)
            return "should-not-run"

        self.pipeline.register_handler(
            CommandType.START_RESEARCH,
            handler,
        )

        result = self.pipeline.execute(
            self.viewer,
            "Research this case.",
        )

        self.assertTrue(result.validation.valid)
        self.assertFalse(result.authorization.authorized)
        self.assertFalse(result.executed)
        self.assertIsNone(result.dispatch)
        self.assertEqual(
            executions,
            [],
        )

    def test_authorized_command_executes(self):
        self.pipeline.register_handler(
            CommandType.START_RESEARCH,
            lambda command: "research-started",
        )

        result = self.pipeline.execute(
            self.operator,
            "Research this case.",
        )

        self.assertTrue(result.authorization.authorized)
        self.assertTrue(result.executed)
        self.assertTrue(result.dispatch.success)
        self.assertEqual(
            result.dispatch.data,
            "research-started",
        )

    def test_handler_failure_remains_visible(self):
        def handler(command):
            raise RuntimeError(
                "provider unavailable"
            )

        self.pipeline.register_handler(
            CommandType.START_RESEARCH,
            handler,
        )

        result = self.pipeline.execute(
            self.operator,
            "Research this case.",
        )

        self.assertTrue(result.authorization.authorized)
        self.assertTrue(result.executed)
        self.assertIsNotNone(result.dispatch)
        self.assertFalse(result.dispatch.success)
        self.assertEqual(
            result.dispatch.error,
            "provider unavailable",
        )

    def test_unknown_request_never_reaches_dispatch(self):
        executions = []

        def handler(command):
            executions.append(command)

        self.pipeline.register_handler(
            CommandType.GET_STATUS,
            handler,
        )

        with self.assertRaises(Exception):
            self.pipeline.execute(
                self.operator,
                "Do something completely unknown.",
            )

        self.assertEqual(
            executions,
            [],
        )


if __name__ == "__main__":
    unittest.main()
