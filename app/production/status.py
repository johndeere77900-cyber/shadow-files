"""
Shadow Files production-status transition rules.

Production stages are deliberately explicit. A production record cannot
silently jump over required review or approval stages.
"""

from app.production.models import ProductionStatus


class InvalidProductionTransition(ValueError):
    """Raised when an invalid production status transition is requested."""


_ALLOWED_TRANSITIONS = {
    ProductionStatus.NOT_STARTED: {
        ProductionStatus.STORY_PLANNING,
        ProductionStatus.BLOCKED,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
    },
    ProductionStatus.STORY_PLANNING: {
        ProductionStatus.SCRIPT_DRAFT,
        ProductionStatus.BLOCKED,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
        ProductionStatus.FAILED,
    },
    ProductionStatus.SCRIPT_DRAFT: {
        ProductionStatus.SCRIPT_REVIEW,
        ProductionStatus.BLOCKED,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
        ProductionStatus.FAILED,
    },
    ProductionStatus.SCRIPT_REVIEW: {
        ProductionStatus.SCRIPT_APPROVED,
        ProductionStatus.SCRIPT_DRAFT,
        ProductionStatus.BLOCKED,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
    },
    ProductionStatus.SCRIPT_APPROVED: {
        ProductionStatus.SCENE_PLANNING,
        ProductionStatus.BLOCKED,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
        ProductionStatus.FAILED,
    },
    ProductionStatus.SCENE_PLANNING: {
        ProductionStatus.PRODUCTION,
        ProductionStatus.BLOCKED,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
        ProductionStatus.FAILED,
    },
    ProductionStatus.PRODUCTION: {
        ProductionStatus.QC,
        ProductionStatus.BLOCKED,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
        ProductionStatus.FAILED,
    },
    ProductionStatus.QC: {
        ProductionStatus.HUMAN_APPROVAL,
        ProductionStatus.PRODUCTION,
        ProductionStatus.BLOCKED,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
        ProductionStatus.FAILED,
    },
    ProductionStatus.HUMAN_APPROVAL: {
        ProductionStatus.READY,
        ProductionStatus.PRODUCTION,
        ProductionStatus.QC,
        ProductionStatus.BLOCKED,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
    },
    ProductionStatus.READY: {
        ProductionStatus.CANCELLED,
    },
    ProductionStatus.BLOCKED: {
        ProductionStatus.STORY_PLANNING,
        ProductionStatus.SCRIPT_DRAFT,
        ProductionStatus.SCRIPT_REVIEW,
        ProductionStatus.SCRIPT_APPROVED,
        ProductionStatus.SCENE_PLANNING,
        ProductionStatus.PRODUCTION,
        ProductionStatus.QC,
        ProductionStatus.HUMAN_APPROVAL,
        ProductionStatus.PAUSED,
        ProductionStatus.CANCELLED,
    },
    ProductionStatus.FAILED: {
        ProductionStatus.STORY_PLANNING,
        ProductionStatus.SCRIPT_DRAFT,
        ProductionStatus.SCENE_PLANNING,
        ProductionStatus.PRODUCTION,
        ProductionStatus.QC,
        ProductionStatus.CANCELLED,
    },
    ProductionStatus.PAUSED: {
        ProductionStatus.STORY_PLANNING,
        ProductionStatus.SCRIPT_DRAFT,
        ProductionStatus.SCRIPT_REVIEW,
        ProductionStatus.SCRIPT_APPROVED,
        ProductionStatus.SCENE_PLANNING,
        ProductionStatus.PRODUCTION,
        ProductionStatus.QC,
        ProductionStatus.HUMAN_APPROVAL,
        ProductionStatus.CANCELLED,
    },
    ProductionStatus.CANCELLED: set(),
}


def validate_transition(
    current: ProductionStatus,
    target: ProductionStatus,
) -> None:
    """
    Validate a requested production-state transition.

    Raises:
        InvalidProductionTransition:
            If the requested transition is not explicitly permitted.
    """

    if not isinstance(current, ProductionStatus):
        raise TypeError(
            "Current status must be a ProductionStatus."
        )

    if not isinstance(target, ProductionStatus):
        raise TypeError(
            "Target status must be a ProductionStatus."
        )

    if target not in _ALLOWED_TRANSITIONS[current]:
        raise InvalidProductionTransition(
            f"Invalid production transition: "
            f"{current.value} -> {target.value}"
        )


def allowed_transitions(
    current: ProductionStatus,
) -> frozenset[ProductionStatus]:
    """Return the allowed next states for a production status."""

    if not isinstance(current, ProductionStatus):
        raise TypeError(
            "Current status must be a ProductionStatus."
        )

    return frozenset(
        _ALLOWED_TRANSITIONS[current]
)
