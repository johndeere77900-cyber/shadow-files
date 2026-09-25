"""
Tests for Shadow Files scene planning and production assets.
"""

import unittest

from app.production.assets import (
    AssetStatus,
    AssetType,
    ProductionAsset,
    validate_asset_ready,
)
from app.production.scenes import (
    AudioType,
    Scene,
    ScenePlan,
    VisualType,
    validate_scene_plan,
)
from app.production.script import (
    Script,
    ScriptSegment,
)


class ProductionScenesAssetsTests(unittest.TestCase):

    def setUp(self):
        self.script = Script(
            script_id="script-001",
            story_id="story-001",
            case_id="case-001",
            investigation_id="inv-001",
            segments=(
                ScriptSegment(
                    segment_id="segment-001",
                    section_id="section-001",
                    narration="The case began with a reported disappearance.",
                    claim_ids=("claim-001",),
                ),
            ),
        )

    def test_valid_scene_plan_is_accepted(self):
        scene = Scene(
            scene_id="scene-001",
            script_segment_id="segment-001",
            sequence=1,
            description="Archival photograph",
            visual_type=VisualType.PHOTOGRAPH,
            audio_types=(AudioType.NARRATION,),
        )

        plan = ScenePlan(
            scene_plan_id="scene-plan-001",
            script_id="script-001",
            case_id="case-001",
            scenes=(scene,),
        )

        validate_scene_plan(
            plan,
            self.script,
        )

    def test_scene_rejects_unknown_script_segment(self):
        scene = Scene(
            scene_id="scene-001",
            script_segment_id="segment-999",
            sequence=1,
            description="Archival photograph",
            visual_type=VisualType.PHOTOGRAPH,
        )

        plan = ScenePlan(
            scene_plan_id="scene-plan-001",
            script_id="script-001",
            case_id="case-001",
            scenes=(scene,),
        )

        with self.assertRaises(ValueError):
            validate_scene_plan(
                plan,
                self.script,
            )

    def test_scene_plan_rejects_wrong_script(self):
        plan = ScenePlan(
            scene_plan_id="scene-plan-001",
            script_id="script-other",
            case_id="case-001",
            scenes=(
                Scene(
                    scene_id="scene-001",
                    script_segment_id="segment-001",
                    sequence=1,
                    description="Location image",
                    visual_type=VisualType.LOCATION,
                ),
            ),
        )

        with self.assertRaises(ValueError):
            validate_scene_plan(
                plan,
                self.script,
            )

    def test_source_required_scene_needs_source(self):
        with self.assertRaises(ValueError):
            Scene(
                scene_id="scene-001",
                script_segment_id="segment-001",
                sequence=1,
                description="Document",
                visual_type=VisualType.DOCUMENT,
                source_required=True,
            )

    def test_ready_asset_is_valid(self):
        asset = ProductionAsset(
            asset_id="asset-001",
            production_id="prod-001",
            asset_type=AssetType.VIDEO,
            status=AssetStatus.READY,
            name="Rendered video",
            location="output/video.mp4",
            checksum="checksum-001",
        )

        validate_asset_ready(asset)

    def test_non_ready_asset_is_rejected(self):
        asset = ProductionAsset(
            asset_id="asset-001",
            production_id="prod-001",
            asset_type=AssetType.VIDEO,
            status=AssetStatus.REQUIRED,
            name="Rendered video",
        )

        with self.assertRaises(ValueError):
            validate_asset_ready(asset)

    def test_ready_asset_requires_location(self):
        with self.assertRaises(ValueError):
            ProductionAsset(
                asset_id="asset-001",
                production_id="prod-001",
                asset_type=AssetType.VIDEO,
                status=AssetStatus.READY,
                name="Rendered video",
                checksum="checksum-001",
            )

    def test_ready_asset_requires_checksum(self):
        with self.assertRaises(ValueError):
            ProductionAsset(
                asset_id="asset-001",
                production_id="prod-001",
                asset_type=AssetType.VIDEO,
                status=AssetStatus.READY,
                name="Rendered video",
                location="output/video.mp4",
            )


if __name__ == "__main__":
    unittest.main()
