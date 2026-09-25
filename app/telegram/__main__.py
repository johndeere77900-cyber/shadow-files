"""
Shadow Files Telegram runtime entry point.

This module starts the configured Telegram transport and passes
normalized incoming messages through the Telegram router.

Business execution remains outside the transport layer.
"""

from app.telegram.config import TelegramConfig
from app.telegram.messages import OutgoingMessage
from app.telegram.router import TelegramRouter
from app.telegram.transport import TelegramBotTransport


def main() -> None:
    """Start the Telegram interface."""

    config = TelegramConfig.from_env()

    if not config.enabled:
        print(
            "Shadow Files Telegram interface is disabled."
        )
        return

    if not config.bot_token:
        raise RuntimeError(
            "SHADOW_TELEGRAM_BOT_TOKEN is required "
            "when Telegram is enabled."
        )

    if not config.authorized_chat_id:
        raise RuntimeError(
            "SHADOW_TELEGRAM_AUTHORIZED_CHAT_ID is required "
            "when Telegram is enabled."
        )

    transport = TelegramBotTransport(
        bot_token=config.bot_token,
    )

    router = TelegramRouter(
        authorized_chat_id=config.authorized_chat_id,
    )

    messages = transport.receive()

    for message in messages:
        try:
            route = router.route(message)
        except Exception:
            response = router.unauthorized_response(
                chat_id=message.chat_id,
            )
            transport.send(response)
            continue

        response = OutgoingMessage(
            chat_id=route.message.chat_id,
            text=(
                "Shadow Files received your message: "
                f"{route.message.text}"
            ),
            reply_to_message_id=route.message.message_id,
        )

        transport.send(response)


if __name__ == "__main__":
    main()
