"""
Shadow Files Telegram transport foundation.

This module isolates Telegram transport from the rest of the system.

Actual Telegram API integration will be added only after the interface
contracts and authorization layer have been qualified.
"""

from abc import ABC, abstractmethod

from app.telegram.messages import (
    IncomingMessage,
    OutgoingMessage,
)


class TelegramTransportError(Exception):
    """Raised when Telegram transport fails."""


class TelegramTransport(ABC):
    """Abstract Telegram transport interface."""

    @abstractmethod
    def receive(
        self,
    ) -> list[IncomingMessage]:
        """
        Receive available incoming Telegram messages.

        Concrete implementations must normalize provider-specific
        responses into IncomingMessage objects.
        """

    @abstractmethod
    def send(
        self,
        message: OutgoingMessage,
    ) -> None:
        """
        Send a normalized outgoing Telegram message.
        """


class NullTelegramTransport(TelegramTransport):
    """
    Safe no-op transport used before real Telegram integration.

    It performs no network calls.
    """

    def receive(
        self,
    ) -> list[IncomingMessage]:
        return []

    def send(
        self,
        message: OutgoingMessage,
    ) -> None:
        return None
