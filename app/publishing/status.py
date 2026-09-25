"""
Publication lifecycle states and transition rules for Shadow Files.
"""

from enum import Enum


class PublicationStatus(str, Enum):
    """
    Controlled publication lifecycle.

    A publication cannot move forward by simply changing a string.
    Transitions must follow the rules defined below.
    """

    NOT_STARTED = "NOT_STARTED"
    PACKAGE_READY = "PACKAGE_READY"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"

    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"


ALLOWED_TRANSITIONS = {
    PublicationStatus.NOT_STARTED: {
        PublicationStatus.PACKAGE_READY,
        PublicationStatus.BLOCKED,
        PublicationStatus.CANCELLED,
    },
    PublicationStatus.PACKAGE_READY: {
        PublicationStatus.PENDING_APPROVAL,
        PublicationStatus.BLOCKED,
        PublicationStatus.CANCELLED,
    },
    PublicationStatus.PENDING_APPROVAL: {
        PublicationStatus.APPROVED,
        PublicationStatus.BLOCKED,
        PublicationStatus.PAUSED,
        PublicationStatus.CANCELLED,
    },
    PublicationStatus.APPROVED: {
        PublicationStatus.UPLOADING,
        PublicationStatus.BLOCKED,
        PublicationStatus.PAUSED,
        PublicationStatus.CANCELLED,
    },
    PublicationStatus.UPLOADING: {
        PublicationStatus.UPLOADED,
        PublicationStatus.FAILED,
        PublicationStatus.PAUSED,
    },
    PublicationStatus.UPLOADED: {
        PublicationStatus.SCHEDULED,
        PublicationStatus.PUBLISHED,
        PublicationStatus.FAILED,
        PublicationStatus.PAUSED,
    },
    PublicationStatus.SCHEDULED: {
        PublicationStatus.PUBLISHED,
        PublicationStatus.PAUSED,
        PublicationStatus.CANCELLED,
        PublicationStatus.FAILED,
    },
    PublicationStatus.PUBLISHED: set(),

    PublicationStatus.BLOCKED: {
        PublicationStatus.PACKAGE_READY,
        PublicationStatus.PAUSED,
        PublicationStatus.CANCELLED,
    },
    PublicationStatus.FAILED: {
        PublicationStatus.PACKAGE_READY,
        PublicationStatus.PAUSED,
        PublicationStatus.CANCELLED,
    },
    PublicationStatus.PAUSED: {
        PublicationStatus.PACKAGE_READY,
        PublicationStatus.PENDING_APPROVAL,
        PublicationStatus.APPROVED,
        PublicationStatus.CANCELLED,
    },
    PublicationStatus.CANCELLED: set(),
}


def can_transition(
    current: PublicationStatus,
    target: PublicationStatus,
) -> bool:
    """
    Return whether a publication may move from current to target.
    """

    return target in ALLOWED_TRANSITIONS.get(current, set())


def validate_transition(
    current: PublicationStatus,
    target: PublicationStatus,
) -> None:
    """
    Raise ValueError when a publication transition is invalid.
    """

    if not can_transition(current, target):
        raise ValueError(
            f"Invalid publication transition: "
            f"{current.value} -> {target.value}"
)
