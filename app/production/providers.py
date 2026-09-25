"""
Shadow Files production-provider abstractions.

External AI, narration, media-generation, storage, and rendering
providers must remain replaceable. The production domain depends on
these interfaces rather than directly depending on a specific vendor.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence


class ProviderError(RuntimeError):
    """Base error for production-provider failures."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider cannot currently be used."""


class ProviderValidationError(ProviderError):
    """Raised when provider input fails validation."""


@dataclass(frozen=True)
class ProviderResult:
    """Generic result returned by a production provider."""

    success: bool
    provider_name: str
    output_location: Optional[str] = None
    output_id: Optional[str] = None
    checksum: Optional[str] = None
    notes: str = ""


@dataclass(frozen=True)
class ScriptGenerationRequest:
    """Request for generating a script from verified material."""

    story_id: str
    case_id: str
    verified_claims: Sequence[str]
    story_sections: Sequence[str]
    instructions: str = ""


@dataclass(frozen=True)
class NarrationRequest:
    """Request for converting approved script text into narration."""

    script_id: str
    text: str
    voice_id: Optional[str] = None
    language: str = "en"


@dataclass(frozen=True)
class MediaGenerationRequest:
    """Request for generating or obtaining a production visual."""

    scene_id: str
    description: str
    visual_type: str
    source_ids: Sequence[str] = ()


@dataclass(frozen=True)
class RenderRequest:
    """Request for assembling approved assets into a video."""

    production_id: str
    scene_asset_locations: Sequence[str]
    narration_location: Optional[str] = None
    music_location: Optional[str] = None
    output_format: str = "mp4"


class ScriptProvider(ABC):
    """Provider interface for script-generation services."""

    @abstractmethod
    def generate_script(
        self,
        request: ScriptGenerationRequest,
    ) -> ProviderResult:
        """Generate a script from verified story material."""


class NarrationProvider(ABC):
    """Provider interface for text-to-speech services."""

    @abstractmethod
    def generate_narration(
        self,
        request: NarrationRequest,
    ) -> ProviderResult:
        """Generate narration audio from approved script text."""


class MediaProvider(ABC):
    """Provider interface for visual/media acquisition or generation."""

    @abstractmethod
    def generate_media(
        self,
        request: MediaGenerationRequest,
    ) -> ProviderResult:
        """Generate or acquire media for a scene."""


class RenderProvider(ABC):
    """Provider interface for video rendering/assembly."""

    @abstractmethod
    def render(
        self,
        request: RenderRequest,
    ) -> ProviderResult:
        """Render a production from approved assets."""


class NullScriptProvider(ScriptProvider):
    """
    Safe placeholder provider.

    It deliberately performs no external generation. This allows the
    production engine to be developed and tested before a real provider
    is configured.
    """

    def generate_script(
        self,
        request: ScriptGenerationRequest,
    ) -> ProviderResult:
        raise ProviderUnavailableError(
            "No script-generation provider is configured."
        )


class NullNarrationProvider(NarrationProvider):
    """Safe placeholder for narration until a provider is configured."""

    def generate_narration(
        self,
        request: NarrationRequest,
    ) -> ProviderResult:
        raise ProviderUnavailableError(
            "No narration provider is configured."
        )


class NullMediaProvider(MediaProvider):
    """Safe placeholder for media generation/acquisition."""

    def generate_media(
        self,
        request: MediaGenerationRequest,
    ) -> ProviderResult:
        raise ProviderUnavailableError(
            "No media provider is configured."
        )


class NullRenderProvider(RenderProvider):
    """Safe placeholder for video rendering."""

    def render(
        self,
        request: RenderRequest,
    ) -> ProviderResult:
        raise ProviderUnavailableError(
            "No render provider is configured."
  )
