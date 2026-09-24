"""
Shadow Files Telegram interface tests.

Phase 8 tests authorization, message models, and the safe transport
foundation without making any external Telegram API calls.
"""

import unittest

from app.telegram.authorization import (
    TelegramAuthorizationError,
    authorize_chat,
)
from app.telegram.messages import (
    IncomingMessage,
    OutgoingMessage,
)
from app.telegram.transport import (
    NullTelegramTransport,
)


class TelegramAuthorizationTests(unittest.TestCase):
    """Test Telegram chat authorization."""

    def test_authorized_chat_is_accepted(self) -> None:
        actor = authorize_chat(
            chat_id="123456",
            authorized_chat_id="123456",
        )

        self.assertEqual(
            actor.chat_id,
            "123456",
        )
        self.assertEqual(
            actor.user_id,
            "123456",
        )

    def test_unauthorized_chat_is_rejected(self) -> None:
        with self.assertRaises(
            TelegramAuthorizationError
        ):
            authorize_chat(
                chat_id="999999",
                authorized_chat_id="123456",
            )

    def test_missing_chat_id_is_rejected(self) -> None:
        with self.assertRaises(
            TelegramAuthorizationError
        ):
            authorize_chat(
                chat_id="",
                authorized_chat_id="123456",
            )

    def test_missing_authorized_chat_is_rejected(self) -> None:
        with self.assertRaises(
            TelegramAuthorizationError
        ):
            authorize_chat(
                chat_id="123456",
                authorized_chat_id="",
            )


class TelegramMessageTests(unittest.TestCase):
    """Test normalized Telegram message models."""

    def test_incoming_message_is_created(self) -> None:
        message = IncomingMessage(
            message_id="MSG-001",
            chat_id="123456",
            user_id="123456",
            text="How are we doing?",
            timestamp="2026-09-24T18:00:00+00:00",
        )

        self.assertEqual(
            message.text,
            "How are we doing?",
        )
        self.assertEqual(
            message.chat_id,
            "123456",
        )

    def test_outgoing_message_is_created(self) -> None:
        message = OutgoingMessage(
            chat_id="123456",
            text="Ready. What would you like me to analyze?",
            reply_to_message_id="MSG-001",
        )

        self.assertEqual(
            message.chat_id,
            "123456",
        )
        self.assertEqual(
            message.reply_to_message_id,
            "MSG-001",
        )


class NullTelegramTransportTests(unittest.TestCase):
    """Test the safe no-network Telegram transport."""

    def setUp(self) -> None:
        self.transport = NullTelegramTransport()

    def test_receive_returns_no_messages(self) -> None:
        messages = self.transport.receive()

        self.assertEqual(
            messages,
            [],
        )

    def test_send_does_not_raise(self) -> None:
        message = OutgoingMessage(
            chat_id="123456",
            text="Test message",
        )

        result = self.transport.send(
            message
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
