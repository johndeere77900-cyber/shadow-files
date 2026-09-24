"""
Shadow Files Phase 10 integration qualification tests.

This test verifies the complete controlled command path:

text
-> conversation handling
-> intent validation
-> command mapping
-> command validation
-> authorization
-> dispatch
-> application response
"""

import unittest

from app.commands.models import CommandType
from app.commands.pipeline import CommandPipeline
from app.commands.service import CommandService
from shadow_core.authorization import Actor


class Phase10IntegrationTests(unittest.TestCase):
    """Qualify the complete Phase 10 command execution boundary."""

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

    def test_complete_read_command_path(self):
        self.service.register_handler(
            CommandType.GET_STATUS,
            lambda command: {
                "status": "operational",
            },
        )

        response = self.service.execute(
            self.viewer,
            "How are we doing?",
        )

        self.assertTrue(response.success)

        result = response.result

        self.assertIsNotNone(result)
        self.assertEqual(
            result.intent.intent_type.value,
            "STATUS",
        )
        self.assertEqual(
            result.command.command_type,
            CommandType.GET_STATUS,
        )
        self.assertTrue(
            result.validation.valid
        )
        self.assertTrue(
            result.authorization.authorized
        )
        self.assertTrue(
            result.executed
        )
        self.assertTrue(
            result.dispatch.success
        )
        self.assertEqual(
            result.dispatch.data["status"],
            "operational",
        )

    def test_complete_operational_command_requires_operator(self):
        self.service.register_handler(
            CommandType.START_RESEARCH,
            lambda command: "research-started",
        )

        response = self.service.execute(
            self.viewer,
            "Research this case.",
        )

        self.assertFalse(response.success)

        result = response.result

        self.assertIsNotNone(result)
        self.assertTrue(
            result.validation.valid
        )
        self.assertFalse(
            result.authorization.authorized
        )
        self.assertFalse(
            result.executed
        )
        self.assertIsNone(
            result.dispatch
        )

    def test_complete_operational_command_executes_for_operator(self):
        self.service.register_handler(
            CommandType.START_RESEARCH,
            lambda command: "research-started",
        )

        response = self.service.execute(
            self.operator,
            "Research this case.",
        )

        self.assertTrue(response.success)

        result = response.result

        self.assertIsNotNone(result)
        self.assertEqual(
            result.command.command_type,
            CommandType.START_RESEARCH,
        )
        self.assertTrue(
            result.validation.valid
        )
        self.assertTrue(
            result.authorization.authorized
        )
        self.assertTrue(
            result.executed
        )
        self.assertTrue(
            result.dispatch.success
        )

    def test_unknown_request_cannot_reach_execution(self):
        executions = []

        self.service.register_handler(
            CommandType.GET_STATUS,
            lambda command: executions.append(command),
        )

        response = self.service.execute(
            self.operator,
            "Do something completely unknown.",
        )

        self.assertFalse(response.success)
        self.assertEqual(
            executions,
            [],
        )

    def test_dispatch_failure_does_not_appear_successful(self):
        def failing_handler(command):
            raise RuntimeError(
                "controlled provider failure"
            )

        self.service.register_handler(
            CommandType.START_RESEARCH,
            failing_handler,
        )

        response = self.service.execute(
            self.operator,
            "Research this case.",
        )

        self.assertFalse(response.success)
        self.assertEqual(
            response.message,
            "controlled provider failure",
        )

        result = response.result

        self.assertIsNotNone(result)
        self.assertTrue(
            result.authorization.authorized
        )
        self.assertTrue(
            result.executed
        )
        self.assertFalse(
            result.dispatch.success
        )


if __name__ == "__main__":
    unittest.main()
