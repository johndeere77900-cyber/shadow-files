"""
Tests for Shadow Files production persistence.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.production.assets import (
    AssetStatus,
    AssetType,
    ProductionAsset,
)
from app.production.models import (
    ContentType,
    Production,
    ProductionStatus,
)
from app.production.repository import ProductionRepository
from app.production.assets_repository import ProductionAssetRepository
from database.production_schema import create_production_schema


UTC = timezone.utc


class ProductionRepositoryTests(unittest.TestCase):

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("PRAGMA foreign_keys = ON")

        self.connection.executescript(
            """
            CREATE TABLE cases (
                case_id TEXT PRIMARY KEY
            );
            """
        )

        self.connection.execute(
            """
            INSERT INTO cases (case_id)
            VALUES (?)
            """,
            ("case-001",),
        )

        create_production_schema(self.connection)

        self.repository = ProductionRepository(
            self.connection
        )

        self.asset_repository = ProductionAssetRepository(
            self.connection
        )

    def tearDown(self):
        self.connection.close()

    def _production(self):
        now = datetime.now(UTC)

        return Production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
            status=ProductionStatus.NOT_STARTED,
            created_at=now,
            updated_at=now,
            title="Test Production",
            content_type=ContentType.STORY,
        )

    def test_production_round_trip(self):
        production = self._production()

        self.repository.create(production)

        loaded = self.repository.get(
            "prod-001"
        )

        self.assertIsNotNone(loaded)
        self.assertEqual(
            loaded.production_id,
            production.production_id,
        )
        self.assertEqual(
            loaded.case_id,
            production.case_id,
        )
        self.assertEqual(
            loaded.status,
            ProductionStatus.NOT_STARTED,
        )
        self.assertEqual(
            loaded.title,
            "Test Production",
        )

    def test_unknown_production_returns_none(self):
        loaded = self.repository.get(
            "missing-production"
        )

        self.assertIsNone(loaded)

    def test_status_update_round_trip(self):
        production = self._production()

        self.repository.create(production)

        updated_at = datetime.now(UTC)

        updated = self.repository.update_status(
            production_id="prod-001",
            status=ProductionStatus.STORY_PLANNING,
            updated_at=updated_at,
        )

        self.assertEqual(
            updated.status,
            ProductionStatus.STORY_PLANNING,
        )

        loaded = self.repository.get(
            "prod-001"
        )

        self.assertEqual(
            loaded.status,
            ProductionStatus.STORY_PLANNING,
        )

    def test_list_for_case_returns_productions(self):
        first = self._production()

        second = Production(
            production_id="prod-002",
            case_id="case-001",
            investigation_id="inv-002",
            status=ProductionStatus.NOT_STARTED,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            title="Second Production",
        )

        self.repository.create(first)
        self.repository.create(second)

        productions = self.repository.list_for_case(
            "case-001"
        )

        self.assertEqual(
            len(productions),
            2,
        )

    def test_asset_round_trip(self):
        production = self._production()

        self.repository.create(production)

        asset = ProductionAsset(
            asset_id="asset-001",
            production_id="prod-001",
            asset_type=AssetType.IMAGE,
            status=AssetStatus.DISCOVERED,
            name="Case photograph",
            location="media/photo.jpg",
            source_id="source-001",
            checksum="abc123",
        )

        self.asset_repository.create(asset)

        loaded = self.asset_repository.get(
            "asset-001"
        )

        self.assertIsNotNone(loaded)
        self.assertEqual(
            loaded.asset_id,
            "asset-001",
        )
        self.assertEqual(
            loaded.production_id,
            "prod-001",
        )
        self.assertEqual(
            loaded.asset_type,
            AssetType.IMAGE,
        )
        self.assertEqual(
            loaded.status,
            AssetStatus.DISCOVERED,
        )

    def test_assets_can_be_listed_for_production(self):
        production = self._production()

        self.repository.create(production)

        for asset_id in (
            "asset-001",
            "asset-002",
        ):
            self.asset_repository.create(
                ProductionAsset(
                    asset_id=asset_id,
                    production_id="prod-001",
                    asset_type=AssetType.IMAGE,
                    status=AssetStatus.REQUIRED,
                    name=asset_id,
                )
            )

        assets = self.asset_repository.list_for_production(
            "prod-001"
        )

        self.assertEqual(
            len(assets),
            2,
        )

    def test_asset_status_update_round_trip(self):
        production = self._production()

        self.repository.create(production)

        asset = ProductionAsset(
            asset_id="asset-001",
            production_id="prod-001",
            asset_type=AssetType.VIDEO,
            status=AssetStatus.REQUIRED,
            name="Final video",
        )

        self.asset_repository.create(asset)

        updated = self.asset_repository.update_status(
            "asset-001",
            AssetStatus.READY,
        )

        self.assertEqual(
            updated.status,
            AssetStatus.READY,
        )


if __name__ == "__main__":
    unittest.main()
