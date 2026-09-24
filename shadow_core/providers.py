"""
Shadow Files provider interfaces.

These are abstractions only. No external provider is connected in Phase 6.

The rest of Shadow Files should depend on these interfaces rather than
depending directly on a specific AI, research, voice, image, video, or
storage company.
"""

from abc import ABC, abstractmethod
from typing import Any


class ProviderError(Exception):
    """Base exception for provider-related failures."""


class ResearchProvider(ABC):
    """Interface for external research/source providers."""

    @abstractmethod
    def search(self, query: str) -> Any:
        """Search for research information."""
        raise NotImplementedError


class LLMProvider(ABC):
    """Interface for language-model providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        raise NotImplementedError


class ImageProvider(ABC):
    """Interface for image-generation providers."""

    @abstractmethod
    def generate(self, prompt: str) -> Any:
        """Generate or retrieve an image."""
        raise NotImplementedError


class VoiceProvider(ABC):
    """Interface for voice-synthesis providers."""

    @abstractmethod
    def synthesize(self, text: str) -> Any:
        """Convert text into voice/audio."""
        raise NotImplementedError


class VideoProvider(ABC):
    """Interface for optional video-generation providers."""

    @abstractmethod
    def generate(self, prompt: str) -> Any:
        """Generate or retrieve video material."""
        raise NotImplementedError


class StorageProvider(ABC):
    """Interface for permanent or production storage."""

    @abstractmethod
    def put(self, key: str, data: bytes) -> str:
        """Store data and return its storage reference."""
        raise NotImplementedError
