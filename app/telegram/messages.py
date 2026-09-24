"""
Shadow Files Telegram message models.

This module defines the internal representation of incoming and outgoing
Telegram messages. Telegram-specific transport logic stays separate.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class IncomingMessage:
    """A normalized incoming Telegram message."""

    message_id: str
    chat_id: str
    user_id: str
    text: str
    timestamp: str


@dataclass(frozen=True)
class OutgoingMessage:
    """A normalized outgoing Telegram message."""

    chat_id: str
    text: str
    reply_to_message_id: Optional[str] = None
