"""
Shadow Files command-layer tests.

Phase 10 verifies command mapping, validation, and controlled
dispatcher behavior without executing real business operations.
"""

import unittest

from app.commands.dispatcher import (
    CommandDispatchError,
    CommandDispatcher,
)
from app.commands.mapping import (
    CommandMappingError,
    map_intent_to_command,
)
from app.commands.models import (
    Command,
    CommandType,
)
from app.commands.validation import (
    CommandValidator,
)
from app.conversation.intents import (
    Intent,
    IntentType,
)


class CommandMappingTests(unittest.TestCase):
    """Test intent-to-command mapping."""

    def test_status_maps_to_get_status(self):
        intent = Intent(
            intent_type=IntentType.STATUS,
            raw_text="How are we doing?",
        )

        command = map_intent_to_command(intent)

        self.assertEqual(
            command.command_type,
            CommandType.GET_STATUS,
        )

    def test_research_maps_to_start_research(self):
        intent = Intent(
            intent_type=IntentType.RESEARCH,
            raw_text="Research this case.",
        )

        command = map_intent_to_command(intent)

        self.assertEqual(
            command.command_type,
            CommandType.START_RESEARCH,
        )

    def test_analyze_maps_to_analyze_case(self):
        intent = Intent(
            intent_type=IntentType.ANALYZE,
            raw_text="Analyze this case.",
        )

        command = map_intent_to_command(intent)

        self.assertEqual(
            command.command_type,
            CommandType.ANALYZE_CASE,
        )

    def test_unknown_intent_cannot_be_mapped(self):
        intent = Intent(
            intent_type=IntentType.UNKNOWN,
            raw_text="Do something.",
        )

        with self.assertRaises(CommandMappingError):
            map_intent_to_command(intent)

    def test_mapping_preserves_target_and_parameters(self):
        intent = Intent(
            intent_type=IntentType.CONTINUE_CASE,
            raw_text="Continue case.",
            target="case-001",
            parameters=(
                ("priority", "normal"),
            ),
        )

        command = map_intent_to_command(intent)

        self.assertEqual(
            command.target,
            "case-001",
        )
        self.assertEqual(
            command.parameters,
            (("priority", "normal"),),
        )


class CommandValidationTests(unittest.TestCase):
    """Test command validation."""

    def test_valid_command_is_accepted(self):
        command = Command(
            command_type=CommandType.GET_STATUS,
            source_intent="STATUS",
        )

        result = CommandValidator().validate(command)

        self.assertTrue(result.valid)
        self.assertEqual(result.reason, "")

    def test_missing_source_intent_is_rejected(self):
        command = Command(
            command_type=CommandType.GET_STATUS,
            source_intent="",
        )

        result = CommandValidator().validate(command)

        self.assertFalse(result.valid)
        self.assertIn(
            "source intent",
            result.reason.lower(),
        )

    def test_invalid_parameters_type_is_rejected(self):
        command = Command(
            command_type=CommandType.GET_STATUS,
            source_intent="STATUS",
            parameters=[],
        )

        result = CommandValidator().validate(command)

        self.assertFalse(result.valid)
        self.assertIn(
            "parameters",
            result.reason.lower(),
        )


class CommandDispatcherTests(unittest.TestCase):
    """Test controlled command dispatch."""

    def test_registered_handler_is_executed(self):
        dispatcher = CommandDispatcher()

        def handler(command):
            return "status-ok"

        dispatcher.register(
            CommandType.GET_STATUS,
            handler,
        )

        command = Command(
            command_type=CommandType.GET_STATUS,
            source_intent="STATUS",
        )

        result = dispatcher.dispatch(command)

        self.assertTrue(result.success)
        self.assertEqual(
            result.data,
            "status-ok",
        )

    def test_unregistered_command_is_rejected(self):
        dispatcher = CommandDispatcher()

        command = Command(
            command_type=CommandType.GET_STATUS,
            source_intent="STATUS",
        )

        with self.assertRaises(CommandDispatchError):
            dispatcher.dispatch(command)

    def test_handler_failure_returns_failed_result(self):
        dispatcher = CommandDispatcher()

        def handler(command):
            raise RuntimeError("controlled failure")

        dispatcher.register(
            CommandType.GET_STATUS,
            handler,
        )

        command = Command(
            command_type=CommandType.GET_STATUS,
            source_intent="STATUS",
        )

        result = dispatcher.dispatch(command)

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "controlled failure",
        )

    def test_non_callable_handler_is_rejected(self):
        dispatcher = CommandDispatcher()

        with self.assertRaises(CommandDispatchError):
            dispatcher.register(
                CommandType.GET_STATUS,
                "not-a-handler",
            )


if __name__ == "__main__":
    unittest.main()
