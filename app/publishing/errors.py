"""
Publishing-specific exceptions for Shadow Files.
"""


class PublishingError(Exception):
    """Base exception for publishing failures."""


class PublicationValidationError(PublishingError):
    """Raised when publication data or prerequisites are invalid."""


class PublicationStateError(PublishingError):
    """Raised when an invalid publication state transition is attempted."""


class PublicationApprovalError(PublishingError):
    """Raised when publication approval requirements are not satisfied."""


class PublisherUnavailableError(PublishingError):
    """Raised when the requested publishing provider is unavailable."""


class UploadError(PublishingError):
    """Raised when a video upload fails."""


class SchedulingError(PublishingError):
    """Raised when YouTube scheduling fails."""


class PublicationNotFoundError(PublishingError):
    """Raised when a requested publication record does not exist."""
