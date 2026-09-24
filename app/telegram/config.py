"""
Shadow Files Telegram configuration.

Telegram credentials and runtime settings are loaded from environment
variables. Secrets must never be stored in the repository.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class TelegramConfig:
    """Telegram interface configuration."""

    enabled: bool = False
    bot_token: str = ""
    authorized_chat_id: str = ""

    @classmethod
    def from_env(cls) -> "TelegramConfig":
        """Create Telegram configuration from environment variables."""

        return cls(
            enabled=os.getenv(
                "SHADOW_TELEGRAM_ENABLED",
                "false",
            ).lower() == "true",
            bot_token=os.getenv(
                "SHADOW_TELEGRAM_BOT_TOKEN",
                "",
            ),
            authorized_chat_id=os.getenv(
                "SHADOW_TELEGRAM_AUTHORIZED_CHAT_ID",
                "",
            ),
                )
