"""
Tests for Shadow Files production service orchestration.
"""

import sqlite3
import unittest

from app.production.models import ProductionStatus
from app.production.repository import ProductionRepository
from app.production.service import ProductionService
from database.production_schema import create_production_schema


class ProductionServiceTests(unittest.TestCase):

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

        create_production_schema(
            self.connection
        )

        self.repository = ProductionRepository(
            self.connection
        )

        self.service = ProductionService(
            self.repository
        )

    def tearDown(self):
        self.connection.close()

    def test_create_production_starts_not_started(self):
        production = self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
            title="Test Case",
        )

        self.assertEqual(
            production.status,
            ProductionStatus.NOT_STARTED,
        )

        loaded = self.service.get_production(
            "prod-001"
        )

        self.assertIsNotNone(loaded)
        self.assertEqual(
            loaded.status,
            ProductionStatus.NOT_STARTED,
        )

    def test_full_controlled_lifecycle(self):
        self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
        )

        self.service.start_story_planning(
            "prod-001"
        )

        self.service.start_script_draft(
            "prod-001"
        )

        self.service.submit_script_for_review(
            "prod-001"
        )

        self.service.approve_script(
            "prod-001"
        )

        self.service.start_scene_planning(
            "prod-001"
        )

        self.service.start_production(
            "prod-001"
        )

        self.service.submit_for_qc(
            "prod-001"
        )

        self.service.submit_for_human_approval(
            "prod-001"
        )

        final = self.service.mark_ready(
            "prod-001"
        )

        self.assertEqual(
            final.status,
            ProductionStatus.READY,
        )

    def test_invalid_lifecycle_jump_is_rejected(self):
        self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
        )

        with self.assertRaises(ValueError):
            self.service.mark_ready(
                "prod-001"
            )

    def test_block_and_resume(self):
        self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
        )

        blocked = self.service.block(
            "prod-001"
        )

        self.assertEqual(
            blocked.status,
            ProductionStatus.BLOCKED,
        )

        resumed = self.service.start_story_planning(
            "prod-001"
        )

        self.assertEqual(
            resumed.status,
            ProductionStatus.STORY_PLANNING,
        )

    def test_pause_and_resume(self):
        self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
        )

        paused = self.service.pause(
            "prod-001"
        )

        self.assertEqual(
            paused.status,
            ProductionStatus.PAUSED,
        )

        resumed = self.service.start_story_planning(
            "prod-001"
        )

        self.assertEqual(
            resumed.status,
            ProductionStatus.STORY_PLANNING,
        )

    def test_cancelled_production_cannot_resume(self):
        self.service.create_production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
        )

        cancelled = self.service.cancel(
            "prod-001"
        )

        self.assertEqual(
            cancelled.status,
            ProductionStatus.CANCELLED,
        )

        with self.assertRaises(ValueError):
            self.service.start_story_planning(
                "prod-001"
            )

    def test_missing_production_is_rejected(self):
        with self.assertRaises(KeyError):
            self.service.start_story_planning(
                "missing-production"
            )


if __name__ == "__main__":
    unittest.main()
