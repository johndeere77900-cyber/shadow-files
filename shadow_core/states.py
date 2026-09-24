"""
Shadow Files case state machine foundation.

This module defines the controlled lifecycle of a Shadow Files case.
"""

from enum import Enum


class CaseState(str, Enum):
    """All recognized case lifecycle states."""

    IDEA = "IDEA"
    CASE_SELECTED = "CASE_SELECTED"

    RESEARCHING = "RESEARCHING"
    EVIDENCE_REVIEW = "EVIDENCE_REVIEW"
    RESEARCH_VERIFIED = "RESEARCH_VERIFIED"

    STORY_PLANNING = "STORY_PLANNING"

    SCRIPT_DRAFT = "SCRIPT_DRAFT"
    SCRIPT_REVIEW = "SCRIPT_REVIEW"
    SCRIPT_APPROVED = "SCRIPT_APPROVED"

    SCENE_PLANNING = "SCENE_PLANNING"
    PRODUCTION = "PRODUCTION"
    QC = "QC"

    HUMAN_APPROVAL = "HUMAN_APPROVAL"

    UPLOAD = "UPLOAD"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"

    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"


class InvalidTransition(Exception):
    """Raised when a case attempts an unauthorized state transition."""


MAIN_TRANSITIONS = {
    CaseState.IDEA: {
        CaseState.CASE_SELECTED,
    },

    CaseState.CASE_SELECTED: {
        CaseState.RESEARCHING,
    },

    CaseState.RESEARCHING: {
        CaseState.EVIDENCE_REVIEW,
    },

    CaseState.EVIDENCE_REVIEW: {
        CaseState.RESEARCH_VERIFIED,
    },

    CaseState.RESEARCH_VERIFIED: {
        CaseState.STORY_PLANNING,
    },

    CaseState.STORY_PLANNING: {
        CaseState.SCRIPT_DRAFT,
    },

    CaseState.SCRIPT_DRAFT: {
        CaseState.SCRIPT_REVIEW,
    },

    CaseState.SCRIPT_REVIEW: {
        CaseState.SCRIPT_APPROVED,
    },

    CaseState.SCRIPT_APPROVED: {
        CaseState.SCENE_PLANNING,
    },

    CaseState.SCENE_PLANNING: {
        CaseState.PRODUCTION,
    },

    CaseState.PRODUCTION: {
        CaseState.QC,
    },

    CaseState.QC: {
        CaseState.HUMAN_APPROVAL,
    },

    CaseState.HUMAN_APPROVAL: {
        CaseState.UPLOAD,
    },

    CaseState.UPLOAD: {
        CaseState.SCHEDULED,
    },

    CaseState.SCHEDULED: {
        CaseState.PUBLISHED,
    },
}


def can_transition(
    current: CaseState,
    target: CaseState,
) -> bool:
    """Return True when the requested transition is allowed."""

    return target in MAIN_TRANSITIONS.get(current, set())


def transition(
    current: CaseState,
    target: CaseState,
) -> CaseState:
    """
    Perform a validated state transition.

    Invalid transitions are rejected instead of being silently accepted.
    """

    if not can_transition(current, target):
        raise InvalidTransition(
            f"Invalid transition: {current.value} -> {target.value}"
        )

    return target
