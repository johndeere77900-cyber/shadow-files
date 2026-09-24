"""
Shadow Files Telegram router tests.

These tests verify that the router authorizes incoming messages before
allowing them into the application layer.
"""

import unittest

from app.telegram.authorization import (
    TelegramAuthorizationError,
)
from app.telegram.messages import (
    IncomingMessage,
)
from app.telegram.router import (
    TelegramRouter,
)


class TelegramRouterTests(unittest.TestCase):
    """Test Telegram message routing."""

    def setUp(self) -> None:
        self.router = TelegramRouter(
            authorized_chat_id="123456"
        )

    def test_authorized_message_is_routed(self) -> None:
        message = IncomingMessage(
            message_id="MSG-001",
            chat_id="123456",
            user_id="123456",
            text="How are we doing?",
            timestamp="2026-09-24T18:00:00+00:00",
        )

        route = self.router.route(message)

        self.assertEqual(
            route.actor.chat_id,
            "123456",
        )
        self.assertEqual(
            route.message.message_id,
            "MSG-001",
        )
        self.assertEqual(
            route.message.text,
            "How are we doing?",
        )

    def test_unauthorized_message_is_rejected(self) -> None:
        message = IncomingMessage(
            message_id="MSG-002",
            chat_id="999999",
            user_id="999999",
            text="Run something",
            timestamp="2026-09-24T18:01:00+00:00",
        )

        with self.assertRaises(
            TelegramAuthorizationError
        ):
            self.router.route(message)

    def test_unauthorized_response_is_safe(self) -> None:
        response = self.router.unauthorized_response(
            chat_id="999999"
        )

        self.assertEqual(
            response.chat_id,
            "999999",
        )
        self.assertIn(
            "not authorized",
            response.text,
        )


if __name__ == "__main__":
    unittest.main()
