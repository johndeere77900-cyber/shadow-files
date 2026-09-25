"""
Shadow Files Telegram transport.

This module provides the real Telegram Bot API transport while keeping
Telegram-specific HTTP handling isolated from the rest of Shadow Files.

The transport does not authorize users and does not execute business
operations. Authorization remains the responsibility of TelegramRouter.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.telegram.messages import (
    IncomingMessage,
    OutgoingMessage,
)


class TelegramTransportError(Exception):
    """Raised when Telegram transport fails."""


class TelegramTransport(ABC):
    """Abstract Telegram transport interface."""

    @abstractmethod
    def receive(self) -> list[IncomingMessage]:
        """Receive available Telegram messages."""

    @abstractmethod
    def send(self, message: OutgoingMessage) -> None:
        """Send a Telegram message."""


class TelegramBotTransport(TelegramTransport):
    """
    Telegram Bot API transport.

    Uses long-polling through getUpdates for the initial live runtime.
    Telegram-specific API responses are normalized into Shadow Files
    message models before leaving this class.
    """

    def __init__(
        self,
        bot_token: str,
        timeout: int = 30,
    ) -> None:
        if not bot_token:
            raise ValueError("bot_token is required.")

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        self.bot_token = bot_token
        self.timeout = timeout
        self._offset: int | None = None

    @property
    def api_base_url(self) -> str:
        """Return the Telegram Bot API base URL."""

        return f"https://api.telegram.org/bot{self.bot_token}"

    def receive(self) -> list[IncomingMessage]:
        """
        Retrieve pending Telegram updates.

        Only text messages are normalized. Other Telegram update types
        are ignored at this application boundary.
        """

        params: dict[str, object] = {
            "timeout": self.timeout,
        }

        if self._offset is not None:
            params["offset"] = self._offset

        response = self._request(
            method="getUpdates",
            payload=params,
        )

        updates = response.get("result", [])

        messages: list[IncomingMessage] = []

        for update in updates:
            update_id = update.get("update_id")

            if isinstance(update_id, int):
                self._offset = update_id + 1

            message = update.get("message")

            if not isinstance(message, dict):
                continue

            text = message.get("text")

            if not isinstance(text, str):
                continue

            chat = message.get("chat", {})
            user = message.get("from", {})

            chat_id = chat.get("id")
            user_id = user.get("id")

            if chat_id is None or user_id is None:
                continue

            message_id = message.get("message_id")

            if message_id is None:
                continue

            timestamp = message.get("date")

            if isinstance(timestamp, int):
                message_timestamp = datetime.fromtimestamp(
                    timestamp,
                    tz=timezone.utc,
                ).isoformat()
            else:
                message_timestamp = datetime.now(
                    timezone.utc,
                ).isoformat()

            messages.append(
                IncomingMessage(
                    message_id=str(message_id),
                    chat_id=str(chat_id),
                    user_id=str(user_id),
                    text=text,
                    timestamp=message_timestamp,
                )
            )

        return messages

    def send(
        self,
        message: OutgoingMessage,
    ) -> None:
        """Send a normalized message through Telegram."""

        payload: dict[str, object] = {
            "chat_id": message.chat_id,
            "text": message.text,
        }

        if message.reply_to_message_id is not None:
            payload["reply_parameters"] = {
                "message_id": int(message.reply_to_message_id),
            }

        self._request(
            method="sendMessage",
            payload=payload,
        )

    def _request(
        self,
        method: str,
        payload: dict[str, object],
    ) -> dict:
        """Perform one Telegram Bot API request."""

        url = f"{self.api_base_url}/{method}"

        body = json.dumps(payload).encode("utf-8")

        request = Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout + 5,
            ) as response:
                raw = response.read().decode("utf-8")

        except HTTPError as exc:
            raise TelegramTransportError(
                f"Telegram HTTP request failed: {exc.code}"
            ) from exc

        except URLError as exc:
            raise TelegramTransportError(
                f"Telegram network request failed: {exc.reason}"
            ) from exc

        except TimeoutError as exc:
            raise TelegramTransportError(
                "Telegram request timed out."
            ) from exc

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TelegramTransportError(
                "Telegram returned invalid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise TelegramTransportError(
                "Telegram returned an invalid response."
            )

        if result.get("ok") is not True:
            description = result.get(
                "description",
                "Unknown Telegram API error.",
            )
            raise TelegramTransportError(
                str(description)
            )

        return result


class NullTelegramTransport(TelegramTransport):
    """
    Safe no-op transport retained for tests and disabled environments.

    It performs no network calls.
    """

    def receive(self) -> list[IncomingMessage]:
        return []

    def send(
        self,
        message: OutgoingMessage,
    ) -> None:
        return None
