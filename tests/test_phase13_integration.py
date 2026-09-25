"""
Phase 13 integration tests.

Validates the complete production-domain foundation from production
creation through controlled lifecycle progression, asset tracking,
and lifecycle event recording.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.production.assets import (
    AssetStatus,
    AssetType,
    ProductionAsset,
)
from app.production.assets_repository import (
    ProductionAssetRepository,
)
from app.production.events import (
    ProductionEvent,
    ProductionEventRepository,
)
from app.production.models import ProductionStatus
from app.production.repository import ProductionRepository
from app.production.service import ProductionService
from database.production_schema import create_production_schema


UTC = timezone.utc


class Phase13IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

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

        create_production_schema(
            self.connection
        )

        self.production_repository = ProductionRepository(
            self.connection
        )

        self.asset_repository = ProductionAssetRepository(
            self.connection
        )

        self.event_repository = ProductionEventRepository(
            self.connection
        )

        self.service = ProductionService(
            self.production_repository
        )

    def tearDown(self):
        self.connection.close()

    def test_complete_production_flow(self):
        production = self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
            title="Shadow Files Test Production",
        )

        self.assertEqual(
            production.status,
            ProductionStatus.NOT_STARTED,
        )

        transitions = [
            self.service.start_story_planning,
            self.service.start_script_draft,
            self.service.submit_script_for_review,
            self.service.approve_script,
            self.service.start_scene_planning,
            self.service.start_production,
            self.service.submit_for_qc,
            self.service.submit_for_human_approval,
            self.service.mark_ready,
        ]

        for transition in transitions:
            production = transition(
                "prod-001"
            )

        self.assertEqual(
            production.status,
            ProductionStatus.READY,
        )

        stored = self.production_repository.get(
            "prod-001"
        )

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.status,
            ProductionStatus.READY,
        )

    def test_production_can_have_assets(self):
        self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
        )

        asset = ProductionAsset(
            asset_id="asset-001",
            production_id="prod-001",
            asset_type=AssetType.VIDEO,
            status=AssetStatus.READY,
            name="Final rendered video",
            location="output/final.mp4",
            checksum="checksum-001",
        )

        self.asset_repository.create(
            asset
        )

        stored_assets = (
            self.asset_repository.list_for_production(
                "prod-001"
            )
        )

        self.assertEqual(
            len(stored_assets),
            1,
        )

        self.assertEqual(
            stored_assets[0].status,
            AssetStatus.READY,
        )

    def test_production_events_are_auditable(self):
        self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
        )

        event_time = datetime.now(UTC)

        event = ProductionEvent(
            event_id="event-001",
            production_id="prod-001",
            from_status=ProductionStatus.NOT_STARTED.value,
            to_status=ProductionStatus.STORY_PLANNING.value,
            occurred_at=event_time,
            reason="Production workflow started.",
        )

        self.event_repository.create(
            event
        )

        events = (
            self.event_repository.list_for_production(
                "prod-001"
            )
        )

        self.assertEqual(
            len(events),
            1,
        )

        self.assertEqual(
            events[0].event_id,
            "event-001",
        )

        self.assertEqual(
            events[0].from_status,
            ProductionStatus.NOT_STARTED.value,
        )

        self.assertEqual(
            events[0].to_status,
            ProductionStatus.STORY_PLANNING.value,
        )

    def test_foreign_key_prevents_orphan_production(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                """
                INSERT INTO productions (
                    production_id,
                    case_id,
                    investigation_id,
                    status,
                    title,
                    content_type,
                    notes,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "prod-orphan",
                    "case-missing",
                    "inv-001",
                    ProductionStatus.NOT_STARTED.value,
                    None,
                    None,
                    "",
                    datetime.now(UTC).isoformat(),
                    datetime.now(UTC).isoformat(),
                ),
            )

    def test_production_cascade_removes_assets_and_events(self):
        self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
        )

        self.asset_repository.create(
            ProductionAsset(
                asset_id="asset-001",
                production_id="prod-001",
                asset_type=AssetType.IMAGE,
                status=AssetStatus.REQUIRED,
                name="Evidence image",
            )
        )

        self.event_repository.create(
            ProductionEvent(
                event_id="event-001",
                production_id="prod-001",
                from_status=None,
                to_status=ProductionStatus.NOT_STARTED.value,
                occurred_at=datetime.now(UTC),
                reason="Production created.",
            )
        )

        self.connection.execute(
            """
            DELETE FROM productions
            WHERE production_id = ?
            """,
            ("prod-001",),
        )
        self.connection.commit()

        assets = (
            self.asset_repository.list_for_production(
                "prod-001"
            )
        )

        events = (
            self.event_repository.list_for_production(
                "prod-001"
            )
        )

        self.assertEqual(
            assets,
            [],
        )

        self.assertEqual(
            events,
            [],
        )


if __name__ == "__main__":
    unittest.main()
