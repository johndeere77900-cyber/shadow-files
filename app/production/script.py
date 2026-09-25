"""
Shadow Files script-domain models and validation.

Scripts are generated from an approved story plan and verified claims.
This module does not perform external AI generation; providers will be
connected through the production service layer.
"""

from dataclasses import dataclass
from typing import Tuple

from app.production.story import StoryPlan


@dataclass(frozen=True)
class ScriptSegment:
    """A single segment of the final narration script."""

    segment_id: str
    section_id: str
    narration: str
    claim_ids: Tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.segment_id.strip():
            raise ValueError("Script segment ID is required.")

        if not self.section_id.strip():
            raise ValueError("Script section ID is required.")

        if not self.narration.strip():
            raise ValueError("Script narration is required.")

        if not isinstance(self.claim_ids, tuple):
            raise TypeError(
                "Script claim_ids must be a tuple."
            )

        for claim_id in self.claim_ids:
            if not isinstance(claim_id, str) or not claim_id.strip():
                raise ValueError(
                    "Script claim IDs must be non-empty strings."
                )


@dataclass(frozen=True)
class Script:
    """Immutable script generated from an approved story plan."""

    script_id: str
    story_id: str
    case_id: str
    investigation_id: str
    segments: Tuple[ScriptSegment, ...]
    version: int = 1
    approved: bool = False

    def __post_init__(self) -> None:
        if not self.script_id.strip():
            raise ValueError("Script ID is required.")

        if not self.story_id.strip():
            raise ValueError("Story ID is required.")

        if not self.case_id.strip():
            raise ValueError("Case ID is required.")

        if not self.investigation_id.strip():
            raise ValueError(
                "Investigation ID is required."
            )

        if not self.segments:
            raise ValueError(
                "A script must contain at least one segment."
            )

        if not isinstance(self.segments, tuple):
            raise TypeError(
                "Script segments must be provided as a tuple."
            )

        if not isinstance(self.version, int):
            raise TypeError(
                "Script version must be an integer."
            )

        if self.version < 1:
            raise ValueError(
                "Script version must be at least 1."
            )

        if not isinstance(self.approved, bool):
            raise TypeError(
                "Script approved flag must be boolean."
            )


def validate_script_against_story(
    script: Script,
    story_plan: StoryPlan,
) -> None:
    """
    Validate that a script belongs to the supplied story plan and does
    not introduce claims outside the story's verified claim set.
    """

    if script.story_id != story_plan.story_id:
        raise ValueError(
            "Script does not belong to the supplied story plan."
        )

    if script.case_id != story_plan.case_id:
        raise ValueError(
            "Script case does not match the story plan."
        )

    if (
        script.investigation_id
        != story_plan.investigation_id
    ):
        raise ValueError(
            "Script investigation does not match the story plan."
        )

    verified = set(
        story_plan.verified_claim_ids
    )

    for segment in script.segments:
        for claim_id in segment.claim_ids:
            if claim_id not in verified:
                raise ValueError(
                    "Script references an unverified claim: "
                    f"{claim_id}"
  )
