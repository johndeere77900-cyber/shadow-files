"""
Shadow Files scene-planning models and validation.

A scene plan translates an approved script into production requirements.
It does not create media itself.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class VisualType(str, Enum):
    """Supported categories of visual material."""

    ARCHIVAL = "ARCHIVAL"
    PHOTOGRAPH = "PHOTOGRAPH"
    DOCUMENT = "DOCUMENT"
    MAP = "MAP"
    LOCATION = "LOCATION"
    RECONSTRUCTION = "RECONSTRUCTION"
    GRAPHIC = "GRAPHIC"
    TEXT = "TEXT"
    STOCK = "STOCK"
    VIDEO = "VIDEO"


class AudioType(str, Enum):
    """Supported categories of audio material."""

    NARRATION = "NARRATION"
    MUSIC = "MUSIC"
    AMBIENCE = "AMBIENCE"
    SOUND_EFFECT = "SOUND_EFFECT"


@dataclass(frozen=True)
class Scene:
    """A single production scene."""

    scene_id: str
    script_segment_id: str
    sequence: int
    description: str
    visual_type: VisualType
    audio_types: Tuple[AudioType, ...] = ()
    source_required: bool = False
    source_ids: Tuple[str, ...] = ()
    notes: str = ""
    estimated_duration_seconds: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.scene_id.strip():
            raise ValueError("Scene ID is required.")

        if not self.script_segment_id.strip():
            raise ValueError(
                "Script segment ID is required."
            )

        if self.sequence < 1:
            raise ValueError(
                "Scene sequence must be at least 1."
            )

        if not self.description.strip():
            raise ValueError(
                "Scene description is required."
            )

        if not isinstance(
            self.visual_type,
            VisualType,
        ):
            raise TypeError(
                "Visual type must be a VisualType."
            )

        if not isinstance(self.audio_types, tuple):
            raise TypeError(
                "Audio types must be provided as a tuple."
            )

        for audio_type in self.audio_types:
            if not isinstance(audio_type, AudioType):
                raise TypeError(
                    "Every audio type must be an AudioType."
                )

        if not isinstance(self.source_required, bool):
            raise TypeError(
                "source_required must be boolean."
            )

        if not isinstance(self.source_ids, tuple):
            raise TypeError(
                "Source IDs must be provided as a tuple."
            )

        if self.source_required and not self.source_ids:
            raise ValueError(
                "A source is required for this scene."
            )

        if (
            self.estimated_duration_seconds is not None
            and self.estimated_duration_seconds <= 0
        ):
            raise ValueError(
                "Estimated scene duration must be positive."
            )


@dataclass(frozen=True)
class ScenePlan:
    """Immutable production scene plan."""

    scene_plan_id: str
    script_id: str
    case_id: str
    scenes: Tuple[Scene, ...]
    version: int = 1

    def __post_init__(self) -> None:
        if not self.scene_plan_id.strip():
            raise ValueError(
                "Scene plan ID is required."
            )

        if not self.script_id.strip():
            raise ValueError(
                "Script ID is required."
            )

        if not self.case_id.strip():
            raise ValueError(
                "Case ID is required."
            )

        if not self.scenes:
            raise ValueError(
                "A scene plan must contain at least one scene."
            )

        if not isinstance(self.scenes, tuple):
            raise TypeError(
                "Scenes must be provided as a tuple."
            )

        if self.version < 1:
            raise ValueError(
                "Scene plan version must be at least 1."
            )


def validate_scene_plan(
    scene_plan: ScenePlan,
    script: object,
) -> None:
    """
    Validate that a scene plan belongs to the supplied script.

    The script object is intentionally accepted structurally here to
    avoid coupling scene planning to a specific script implementation.
    """

    script_id = getattr(script, "script_id", None)
    case_id = getattr(script, "case_id", None)

    if script_id != scene_plan.script_id:
        raise ValueError(
            "Scene plan does not belong to the supplied script."
        )

    if case_id != scene_plan.case_id:
        raise ValueError(
            "Scene plan case does not match the supplied script."
        )

    segment_ids = {
        getattr(segment, "segment_id")
        for segment in getattr(script, "segments", ())
    }

    for scene in scene_plan.scenes:
        if scene.script_segment_id not in segment_ids:
            raise ValueError(
                "Scene references an unknown script segment: "
                f"{scene.script_segment_id}"
)
