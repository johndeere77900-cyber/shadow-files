"""
Shadow Files Telegram runtime entry point.

This module starts the configured Telegram transport and passes
normalized incoming messages through the Telegram router.

Business execution remains outside the transport layer.
"""

from app.telegram.config import TelegramConfig
from app.telegram.router import TelegramRouter
from app.telegram.transport import NullTelegramTransport


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

    # Real Telegram transport will replace this adapter.
    # Keeping the transport boundary explicit prevents Telegram
    # credentials and network logic from entering the application core.
    transport = NullTelegramTransport()

    router = TelegramRouter(
        authorized_chat_id=config.authorized_chat_id,
    )

    messages = transport.receive()

    for message in messages:
        route = router.route(message)
        print(
            f"Received authorized Telegram message "
            f"from {route.actor.chat_id}: {route.message.text}"
        )


if __name__ == "__main__":
    main()
