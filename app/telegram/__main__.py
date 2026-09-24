"""
Shadow Files Telegram interface entry point.

This module intentionally does not connect to Telegram yet.
Actual polling/webhook integration will be introduced only after the
interface foundation has been tested and qualified.
"""

from app.telegram.config import TelegramConfig
from app.telegram.transport import NullTelegramTransport


def main() -> None:
    """Initialize the Telegram interface foundation."""

    config = TelegramConfig.from_env()

    if not config.enabled:
        return

    transport = NullTelegramTransport()

    transport.receive()


if __name__ == "__main__":
    main()
