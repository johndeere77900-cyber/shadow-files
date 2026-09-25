"""
Shadow Files investigation status transitions.

Research must move through explicit states. A failed, incomplete,
or blocked investigation must never be silently treated as verified.
"""

from app.investigation.models import ResearchStatus


class InvalidResearchTransition(Exception):
    """Raised when an invalid research-status transition is attempted."""


RESEARCH_TRANSITIONS = {
    ResearchStatus.NOT_STARTED: {
        ResearchStatus.RESEARCHING,
        ResearchStatus.BLOCKED,
    },
    ResearchStatus.RESEARCHING: {
        ResearchStatus.EVIDENCE_REVIEW,
        ResearchStatus.INCOMPLETE,
        ResearchStatus.BLOCKED,
    },
    ResearchStatus.EVIDENCE_REVIEW: {
        ResearchStatus.VERIFIED,
        ResearchStatus.RESEARCHING,
        ResearchStatus.INCOMPLETE,
        ResearchStatus.BLOCKED,
    },
    ResearchStatus.VERIFIED: set(),
    ResearchStatus.INCOMPLETE: {
        ResearchStatus.RESEARCHING,
        ResearchStatus.BLOCKED,
    },
    ResearchStatus.BLOCKED: {
        ResearchStatus.RESEARCHING,
    },
}


def can_transition(
    current: ResearchStatus,
    target: ResearchStatus,
) -> bool:
    """Return whether a research-status transition is permitted."""

    return target in RESEARCH_TRANSITIONS.get(current, set())


def transition(
    current: ResearchStatus,
    target: ResearchStatus,
) -> ResearchStatus:
    """Perform a validated research-status transition."""

    if not can_transition(current, target):
        raise InvalidResearchTransition(
            f"Invalid research transition: "
            f"{current.value} -> {target.value}"
        )

    return target
