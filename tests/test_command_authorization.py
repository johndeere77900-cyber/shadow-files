"""
Shadow Files command-authorization tests.

Phase 10 verifies that command execution remains protected by the
core authorization boundary.
"""

import unittest

from app.commands.authorization import (
    CommandAuthorizer,
)
from app.commands.models import (
    Command,
    CommandType,
)
from shadow_core.authorization import Actor


class CommandAuthorizationTests(unittest.TestCase):
    """Test command authorization rules."""

    def setUp(self):
        self.authorizer = CommandAuthorizer()

        self.viewer = Actor(
            actor_id="user-001",
            role="viewer",
        )

        self.operator = Actor(
            actor_id="user-002",
            role="operator",
        )

    def test_viewer_can_read_status(self):
        command = Command(
            command_type=CommandType.GET_STATUS,
            source_intent="STATUS",
        )

        result = self.authorizer.authorize(
            self.viewer,
            command,
        )

        self.assertTrue(result.authorized)
        self.assertEqual(result.reason, "")

    def test_viewer_cannot_start_research(self):
        command = Command(
            command_type=CommandType.START_RESEARCH,
            source_intent="RESEARCH",
        )

        result = self.authorizer.authorize(
            self.viewer,
            command,
        )

        self.assertFalse(result.authorized)
        self.assertTrue(result.reason)

    def test_operator_can_start_research(self):
        command = Command(
            command_type=CommandType.START_RESEARCH,
            source_intent="RESEARCH",
        )

        result = self.authorizer.authorize(
            self.operator,
            command,
        )

        self.assertTrue(result.authorized)

    def test_operator_can_change_schedule(self):
        command = Command(
            command_type=CommandType.CHANGE_SCHEDULE,
            source_intent="SCHEDULE_CHANGE",
        )

        result = self.authorizer.authorize(
            self.operator,
            command,
        )

        self.assertTrue(result.authorized)

    def test_viewer_can_show_help(self):
        command = Command(
            command_type=CommandType.SHOW_HELP,
            source_intent="HELP",
        )

        result = self.authorizer.authorize(
            self.viewer,
            command,
        )

        self.assertTrue(result.authorized)

    def test_viewer_cannot_analyze_case(self):
        command = Command(
            command_type=CommandType.ANALYZE_CASE,
            source_intent="ANALYZE",
        )

        result = self.authorizer.authorize(
            self.viewer,
            command,
        )

        self.assertFalse(result.authorized)


if __name__ == "__main__":
    unittest.main()
