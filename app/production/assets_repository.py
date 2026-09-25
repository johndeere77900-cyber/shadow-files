"""
Shadow Files production-asset repository.

Persists production assets independently from the production lifecycle
while maintaining a strict relationship to their production record.
"""

import sqlite3
from typing import Optional

from app.production.assets import (
    AssetStatus,
    AssetType,
    ProductionAsset,
)


class ProductionAssetRepository:
    """Persistence operations for production assets."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def create(
        self,
        asset: ProductionAsset,
    ) -> None:
        """Create a production asset."""

        self._connection.execute(
            """
            INSERT INTO production_assets (
                asset_id,
                production_id,
                asset_type,
                status,
                name,
                location,
                source_id,
                checksum,
                mime_type,
                duration_seconds,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asset.asset_id,
                asset.production_id,
                asset.asset_type.value,
                asset.status.value,
                asset.name,
                asset.location,
                asset.source_id,
                asset.checksum,
                asset.mime_type,
                asset.duration_seconds,
                asset.notes,
            ),
        )
        self._connection.commit()

    def get(
        self,
        asset_id: str,
    ) -> Optional[ProductionAsset]:
        """Return an asset by ID, or None when absent."""

        row = self._connection.execute(
            """
            SELECT
                asset_id,
                production_id,
                asset_type,
                status,
                name,
                location,
                source_id,
                checksum,
                mime_type,
                duration_seconds,
                notes
            FROM production_assets
            WHERE asset_id = ?
            """,
            (asset_id,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def list_for_production(
        self,
        production_id: str,
    ) -> list[ProductionAsset]:
        """Return all assets belonging to a production."""

        rows = self._connection.execute(
            """
            SELECT
                asset_id,
                production_id,
                asset_type,
                status,
                name,
                location,
                source_id,
                checksum,
                mime_type,
                duration_seconds,
                notes
            FROM production_assets
            WHERE production_id = ?
            ORDER BY asset_id ASC
            """,
            (production_id,),
        ).fetchall()

        return [self._from_row(row) for row in rows]

    def update_status(
        self,
        asset_id: str,
        status: AssetStatus,
    ) -> ProductionAsset:
        """Update an asset status."""

        existing = self.get(asset_id)

        if existing is None:
            raise KeyError(
                f"Production asset not found: {asset_id}"
            )

        updated = ProductionAsset(
            asset_id=existing.asset_id,
            production_id=existing.production_id,
            asset_type=existing.asset_type,
            status=status,
            name=existing.name,
            location=existing.location,
            source_id=existing.source_id,
            checksum=existing.checksum,
            mime_type=existing.mime_type,
            duration_seconds=existing.duration_seconds,
            notes=existing.notes,
        )

        self._connection.execute(
            """
            UPDATE production_assets
            SET status = ?
            WHERE asset_id = ?
            """,
            (
                status.value,
                asset_id,
            ),
        )
        self._connection.commit()

        return updated

    @staticmethod
    def _from_row(
        row: sqlite3.Row,
    ) -> ProductionAsset:
        """Convert a database row into a production-asset model."""

        return ProductionAsset(
            asset_id=row["asset_id"],
            production_id=row["production_id"],
            asset_type=AssetType(row["asset_type"]),
            status=AssetStatus(row["status"]),
            name=row["name"],
            location=row["location"],
            source_id=row["source_id"],
            checksum=row["checksum"],
            mime_type=row["mime_type"],
            duration_seconds=row["duration_seconds"],
            notes=row["notes"],
      )
