"""
Tests for Shadow Files production-domain models.

These tests use the project's unittest-based test runner.
"""

import unittest
from datetime import datetime, timedelta, timezone

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
from app.production.scenes import (
    Scene,
    ScenePlan,
    VisualType,
)
from app.production.script import (
    Script,
    ScriptSegment,
)
from app.production.story import (
    StoryPlan,
    StorySection,
)


UTC = timezone.utc


class ProductionModelTests(unittest.TestCase):

    def test_production_accepts_valid_values(self):
        now = datetime.now(UTC)

        production = Production(
            production_id="prod-001",
            case_id="case-001",
            investigation_id="inv-001",
            status=ProductionStatus.NOT_STARTED,
            created_at=now,
            updated_at=now,
            title="Test Case",
            content_type=ContentType.STORY,
        )

        self.assertEqual(
            production.production_id,
            "prod-001",
        )
        self.assertEqual(
            production.status,
            ProductionStatus.NOT_STARTED,
        )

    def test_production_requires_timezone_aware_timestamps(self):
        now = datetime.now()

        with self.assertRaises(ValueError):
            Production(
                production_id="prod-001",
                case_id="case-001",
                investigation_id="inv-001",
                status=ProductionStatus.NOT_STARTED,
                created_at=now,
                updated_at=now,
            )

    def test_production_rejects_reversed_timestamps(self):
        now = datetime.now(UTC)

        with self.assertRaises(ValueError):
            Production(
                production_id="prod-001",
                case_id="case-001",
                investigation_id="inv-001",
                status=ProductionStatus.NOT_STARTED,
                created_at=now,
                updated_at=now - timedelta(seconds=1),
            )

    def test_story_section_requires_identity(self):
        with self.assertRaises(ValueError):
            StorySection(
                section_id="",
                title="Opening",
                purpose="Introduce the case.",
            )

    def test_story_plan_requires_sections(self):
        with self.assertRaises(ValueError):
            StoryPlan(
                story_id="story-001",
                case_id="case-001",
                investigation_id="inv-001",
                sections=(),
            )

    def test_script_segment_requires_narration(self):
        with self.assertRaises(ValueError):
            ScriptSegment(
                segment_id="seg-001",
                section_id="section-001",
                narration="",
            )

    def test_script_requires_segments(self):
        with self.assertRaises(ValueError):
            Script(
                script_id="script-001",
                story_id="story-001",
                case_id="case-001",
                investigation_id="inv-001",
                segments=(),
            )

    def test_scene_requires_description(self):
        with self.assertRaises(ValueError):
            Scene(
                scene_id="scene-001",
                script_segment_id="seg-001",
                sequence=1,
                description="",
                visual_type=VisualType.ARCHIVAL,
            )

    def test_scene_requires_source_when_required(self):
        with self.assertRaises(ValueError):
            Scene(
                scene_id="scene-001",
                script_segment_id="seg-001",
                sequence=1,
                description="Archival photograph",
                visual_type=VisualType.PHOTOGRAPH,
                source_required=True,
            )

    def test_scene_plan_requires_scenes(self):
        with self.assertRaises(ValueError):
            ScenePlan(
                scene_plan_id="plan-001",
                script_id="script-001",
                case_id="case-001",
                scenes=(),
            )

    def test_ready_asset_requires_location_and_checksum(self):
        with self.assertRaises(ValueError):
            ProductionAsset(
                asset_id="asset-001",
                production_id="prod-001",
                asset_type=AssetType.IMAGE,
                status=AssetStatus.READY,
                name="Evidence image",
            )

    def test_valid_ready_asset_is_accepted(self):
        asset = ProductionAsset(
            asset_id="asset-001",
            production_id="prod-001",
            asset_type=AssetType.IMAGE,
            status=AssetStatus.READY,
            name="Evidence image",
            location="media/evidence.jpg",
            checksum="abc123",
        )

        self.assertEqual(
            asset.status,
            AssetStatus.READY,
        )


if __name__ == "__main__":
    unittest.main()
