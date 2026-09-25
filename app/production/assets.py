"""
Shadow Files production-asset models.

Assets represent files or externally referenced media required by a
production. The production engine tracks provenance and readiness but
does not assume a specific storage provider.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AssetType(str, Enum):
    """Categories of production assets."""

    VIDEO = "VIDEO"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    DOCUMENT = "DOCUMENT"
    THUMBNAIL = "THUMBNAIL"
    SUBTITLE = "SUBTITLE"
    OTHER = "OTHER"


class AssetStatus(str, Enum):
    """Lifecycle state of a production asset."""

    REQUIRED = "REQUIRED"
    DISCOVERED = "DISCOVERED"
    READY = "READY"
    MISSING = "MISSING"
    INVALID = "INVALID"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ProductionAsset:
    """Immutable record describing a production asset."""

    asset_id: str
    production_id: str
    asset_type: AssetType
    status: AssetStatus
    name: str
    location: Optional[str] = None
    source_id: Optional[str] = None
    checksum: Optional[str] = None
    mime_type: Optional[str] = None
    duration_seconds: Optional[float] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.asset_id.strip():
            raise ValueError("Asset ID is required.")

        if not self.production_id.strip():
            raise ValueError(
                "Production ID is required."
            )

        if not self.name.strip():
            raise ValueError("Asset name is required.")

        if not isinstance(
            self.asset_type,
            AssetType,
        ):
            raise TypeError(
                "Asset type must be an AssetType."
            )

        if not isinstance(
            self.status,
            AssetStatus,
        ):
            raise TypeError(
                "Asset status must be an AssetStatus."
            )

        if (
            self.duration_seconds is not None
            and self.duration_seconds <= 0
        ):
            raise ValueError(
                "Asset duration must be positive."
            )

        if self.status == AssetStatus.READY:
            if not self.location:
                raise ValueError(
                    "A ready asset must have a location."
                )

            if not self.checksum:
                raise ValueError(
                    "A ready asset must have a checksum."
                )

        if self.source_id is not None:
            if not self.source_id.strip():
                raise ValueError(
                    "Source ID cannot be blank."
                )


def validate_asset_ready(
    asset: ProductionAsset,
) -> None:
    """Raise an error if an asset is not ready for production."""

    if asset.status != AssetStatus.READY:
        raise ValueError(
            f"Asset {asset.asset_id} is not ready: "
            f"{asset.status.value}"
        )

    if not asset.location:
        raise ValueError(
            f"Asset {asset.asset_id} has no location."
        )

    if not asset.checksum:
        raise ValueError(
            f"Asset {asset.asset_id} has no checksum."
  )
