"""
Publication-package validation for Shadow Files.

A publication package is the complete set of assets and metadata
required to hand an approved episode to a human publisher or to an
automated YouTube publisher.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import PublicationValidationError
from .models import PublicationPackage


@dataclass(frozen=True)
class PackageValidationResult:
    """Result of publication-package validation."""

    valid: bool
    errors: tuple[str, ...] = ()


def validate_publication_package(
    package: PublicationPackage,
    *,
    check_files: bool = True,
) -> PackageValidationResult:
    """
    Validate a publication package.

    Metadata is always validated. File existence is checked when
    check_files=True.
    """

    errors: list[str] = []

    if not package.production_id.strip():
        errors.append("production_id is required")

    if not package.title.strip():
        errors.append("title is required")

    if not package.description.strip():
        errors.append("description is required")

    if not package.video_location.strip():
        errors.append("video_location is required")

    if not package.thumbnail_location.strip():
        errors.append("thumbnail_location is required")

    if any(not tag.strip() for tag in package.tags):
        errors.append("tags cannot contain empty values")

    if check_files:
        video_path = Path(package.video_location)
        thumbnail_path = Path(package.thumbnail_location)

        if not video_path.is_file():
            errors.append(
                f"video file does not exist: {package.video_location}"
            )

        if not thumbnail_path.is_file():
            errors.append(
                "thumbnail file does not exist: "
                f"{package.thumbnail_location}"
            )

    return PackageValidationResult(
        valid=not errors,
        errors=tuple(errors),
    )


def require_valid_publication_package(
    package: PublicationPackage,
    *,
    check_files: bool = True,
) -> None:
    """
    Raise PublicationValidationError if the package is invalid.
    """

    result = validate_publication_package(
        package,
        check_files=check_files,
    )

    if not result.valid:
        raise PublicationValidationError(
            "; ".join(result.errors)
  )
