"""
Shadow Files command-service tests.

Phase 10 verifies the application-facing command service and confirms
that authorization and execution failures are exposed safely.
"""

import unittest

from app.commands.models import CommandType
from app.commands.pipeline import CommandPipeline
from app.commands.service import CommandService
from shadow_core.authorization import Actor


class CommandServiceTests(unittest.TestCase):
    """Test the command service."""

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

        self.service = CommandService(
            pipeline=self.pipeline,
        )

    def test_successful_command_returns_success(self):
        self.service.register_handler(
            CommandType.GET_STATUS,
            lambda command: "system-ok",
        )

        response = self.service.execute(
            self.viewer,
            "How are we doing?",
        )

        self.assertTrue(response.success)
        self.assertEqual(
            response.message,
            "Command executed successfully.",
        )
        self.assertIsNotNone(response.result)

    def test_unauthorized_command_returns_safe_failure(self):
        self.service.register_handler(
            CommandType.START_RESEARCH,
            lambda command: "should-not-run",
        )

        response = self.service.execute(
            self.viewer,
            "Research this case.",
        )

        self.assertFalse(response.success)
        self.assertEqual(
            response.message,
            "You are not authorized to execute "
            "this command.",
        )
        self.assertIsNotNone(response.result)

    def test_handler_failure_returns_failure(self):
        def handler(command):
            raise RuntimeError(
                "provider unavailable"
            )

        self.service.register_handler(
            CommandType.START_RESEARCH,
            handler,
        )

        response = self.service.execute(
            self.operator,
            "Research this case.",
        )

        self.assertFalse(response.success)
        self.assertEqual(
            response.message,
            "provider unavailable",
        )

    def test_unknown_command_returns_failure(self):
        response = self.service.execute(
            self.operator,
            "Do something completely unknown.",
        )

        self.assertFalse(response.success)
        self.assertTrue(response.message)


if __name__ == "__main__":
    unittest.main()
