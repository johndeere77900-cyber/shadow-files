"""
Shadow Files Telegram authorization.

Only the configured Telegram chat is permitted to issue commands
through the Telegram interface.
"""

from dataclasses import dataclass


class TelegramAuthorizationError(Exception):
    """Raised when a Telegram request is not authorized."""


@dataclass(frozen=True)
class TelegramActor:
    """Identity of a Telegram user/chat requesting an action."""

    user_id: str
    chat_id: str


def authorize_chat(
    chat_id: str,
    authorized_chat_id: str,
) -> TelegramActor:
    """
    Authorize a Telegram chat.

    Both values must be present and must match exactly.
    """

    if not chat_id:
        raise TelegramAuthorizationError(
            "Telegram chat ID is required."
        )

    if not authorized_chat_id:
        raise TelegramAuthorizationError(
            "No authorized Telegram chat is configured."
        )

    if chat_id != authorized_chat_id:
        raise TelegramAuthorizationError(
            "Telegram chat is not authorized."
        )

    return TelegramActor(
        user_id=chat_id,
        chat_id=chat_id,
      )
