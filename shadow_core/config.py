"""
Shadow Files configuration foundation.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Config:
    """Application configuration loaded from environment variables."""

    app_name: str = "Shadow Files"
    environment: str = "development"
    database_url: str = "sqlite:///shadow_files.db"

    telegram_enabled: bool = False
    youtube_enabled: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""

        return cls(
            app_name=os.getenv(
                "SHADOW_APP_NAME",
                "Shadow Files",
            ),
            environment=os.getenv(
                "SHADOW_ENV",
                "development",
            ),
            database_url=os.getenv(
                "SHADOW_DATABASE_URL",
                "sqlite:///shadow_files.db",
            ),
            telegram_enabled=os.getenv(
                "SHADOW_TELEGRAM_ENABLED",
                "false",
            ).lower() == "true",
            youtube_enabled=os.getenv(
                "SHADOW_YOUTUBE_ENABLED",
                "false",
            ).lower() == "true",
  )
