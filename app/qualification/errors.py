"""
Errors used by the Phase 16 qualification infrastructure.
"""

from __future__ import annotations


class QualificationError(Exception):
    """Base exception for qualification-related failures."""


class QualificationConfigurationError(QualificationError):
    """Raised when qualification configuration is invalid."""


class QualificationExecutionError(QualificationError):
    """Raised when a qualification check cannot be executed."""


class QualificationFailure(QualificationError):
    """Raised when a required qualification condition fails."""


class QualificationReportError(QualificationError):
    """Raised when a qualification report cannot be created or validated."""
