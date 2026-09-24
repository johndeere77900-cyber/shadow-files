"""
Shadow Files Telegram command router.

The router is responsible only for passing an authorized Telegram
message into the application command layer.

Natural-language interpretation and business execution will be added
in later phases.
"""

from dataclasses import dataclass

from app.telegram.authorization import (
    TelegramActor,
    authorize_chat,
)
from app.telegram.messages import (
    IncomingMessage,
    OutgoingMessage,
)


@dataclass(frozen=True)
class TelegramRoute:
    """Result of routing an incoming Telegram message."""

    actor: TelegramActor
    message: IncomingMessage


class TelegramRouter:
    """Authorize and normalize incoming Telegram commands."""

    def __init__(
        self,
        authorized_chat_id: str,
    ) -> None:
        self.authorized_chat_id = authorized_chat_id

    def route(
        self,
        message: IncomingMessage,
    ) -> TelegramRoute:
        """Authorize an incoming message and return its route."""

        actor = authorize_chat(
            chat_id=message.chat_id,
            authorized_chat_id=self.authorized_chat_id,
        )

        return TelegramRoute(
            actor=actor,
            message=message,
        )

    def unauthorized_response(
        self,
        chat_id: str,
    ) -> OutgoingMessage:
        """Create a generic response for unauthorized requests."""

        return OutgoingMessage(
            chat_id=chat_id,
            text="This Telegram chat is not authorized.",
  )
