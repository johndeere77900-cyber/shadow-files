"""
Shadow Files publishing package.

This package provides the controlled publication layer for completed
Shadow Files productions.

Publication supports:
- Human/manual YouTube publication.
- Optional automated YouTube API publication.
- Approval-gated publication.
- Explicit publication lifecycle states.
- Separation between production readiness and actual publication.
"""

from .models import (
    Publication,
    PublicationMode,
    PublicationPackage,
)

from .status import PublicationStatus

__all__ = [
    "Publication",
    "PublicationMode",
    "PublicationPackage",
    "PublicationStatus",
]
