"""
Shadow Files case identity.

A case must have a stable identity so that research, evidence,
scripts, production records, and later updates can refer to the
same investigation without creating accidental duplicates.
"""

from dataclasses import dataclass


class CaseIdentityError(Exception):
    """Raised when case identity cannot be created or validated."""


@dataclass(frozen=True)
class CaseIdentity:
    """Stable identity information for a Shadow Files case."""

    case_id: str
    canonical_title: str

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise CaseIdentityError(
                "Case ID is required."
            )

        if not self.canonical_title.strip():
            raise CaseIdentityError(
                "Canonical case title is required."
            )


def create_case_identity(
    case_id: str,
    canonical_title: str,
) -> CaseIdentity:
    """Create a validated case identity."""

    normalized_id = case_id.strip()
    normalized_title = " ".join(
        canonical_title.split()
    )

    if not normalized_id:
        raise CaseIdentityError(
            "Case ID cannot be empty."
        )

    if not normalized_title:
        raise CaseIdentityError(
            "Canonical case title cannot be empty."
        )

    return CaseIdentity(
        case_id=normalized_id,
        canonical_title=normalized_title,
          )
