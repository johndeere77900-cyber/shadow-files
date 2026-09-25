"""
Shadow Files story-planning models and validation.

Story planning consumes verified investigation information. It does not
perform research and must not introduce unsupported factual claims.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class StorySection:
    """A structured section of a Shadow Files story."""

    section_id: str
    title: str
    purpose: str
    claim_ids: Tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.section_id.strip():
            raise ValueError("Story section ID is required.")

        if not self.title.strip():
            raise ValueError("Story section title is required.")

        if not self.purpose.strip():
            raise ValueError("Story section purpose is required.")

        if not isinstance(self.claim_ids, tuple):
            raise TypeError(
                "Story section claim_ids must be a tuple."
            )

        for claim_id in self.claim_ids:
            if not isinstance(claim_id, str) or not claim_id.strip():
                raise ValueError(
                    "Story section claim IDs must be non-empty strings."
                )


@dataclass(frozen=True)
class StoryPlan:
    """Immutable structure defining the approved story architecture."""

    story_id: str
    case_id: str
    investigation_id: str
    sections: Tuple[StorySection, ...]
    verified_claim_ids: Tuple[str, ...] = ()
    unresolved_items: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.story_id.strip():
            raise ValueError("Story ID is required.")

        if not self.case_id.strip():
            raise ValueError("Case ID is required.")

        if not self.investigation_id.strip():
            raise ValueError(
                "Investigation ID is required."
            )

        if not self.sections:
            raise ValueError(
                "A story plan must contain at least one section."
            )

        if not isinstance(self.sections, tuple):
            raise TypeError(
                "Story sections must be provided as a tuple."
            )

        if not isinstance(self.verified_claim_ids, tuple):
            raise TypeError(
                "Verified claim IDs must be provided as a tuple."
            )

        if not isinstance(self.unresolved_items, tuple):
            raise TypeError(
                "Unresolved items must be provided as a tuple."
            )

        for claim_id in self.verified_claim_ids:
            if not isinstance(claim_id, str) or not claim_id.strip():
                raise ValueError(
                    "Verified claim IDs must be non-empty strings."
                )


def validate_story_claims(
    story_plan: StoryPlan,
) -> None:
    """
    Ensure every claim referenced by a story section belongs to the
    verified-claim set supplied to the story plan.

    This prevents the story layer from silently introducing claims
    that were not part of the verified investigation package.
    """

    verified = set(story_plan.verified_claim_ids)

    for section in story_plan.sections:
        for claim_id in section.claim_ids:
            if claim_id not in verified:
                raise ValueError(
                    "Story section references an unverified claim: "
                    f"{claim_id}"
          )
