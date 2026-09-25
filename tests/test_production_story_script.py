"""
Tests for Shadow Files story and script validation.
"""

import unittest

from app.production.script import (
    Script,
    ScriptSegment,
    validate_script_against_story,
)
from app.production.story import (
    StoryPlan,
    StorySection,
    validate_story_claims,
)


class ProductionStoryScriptTests(unittest.TestCase):

    def setUp(self):
        self.section = StorySection(
            section_id="section-001",
            title="Opening",
            purpose="Introduce the case.",
            claim_ids=("claim-001",),
        )

        self.story = StoryPlan(
            story_id="story-001",
            case_id="case-001",
            investigation_id="inv-001",
            sections=(self.section,),
            verified_claim_ids=("claim-001", "claim-002"),
        )

    def test_valid_story_claims_are_accepted(self):
        validate_story_claims(self.story)

    def test_story_rejects_unverified_claim(self):
        section = StorySection(
            section_id="section-002",
            title="Unverified",
            purpose="Test unsupported material.",
            claim_ids=("claim-999",),
        )

        story = StoryPlan(
            story_id="story-002",
            case_id="case-001",
            investigation_id="inv-001",
            sections=(section,),
            verified_claim_ids=("claim-001",),
        )

        with self.assertRaises(ValueError):
            validate_story_claims(story)

    def test_valid_script_matches_story(self):
        script = Script(
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

        validate_script_against_story(
            script,
            self.story,
        )

    def test_script_rejects_wrong_story(self):
        script = Script(
            script_id="script-001",
            story_id="story-other",
            case_id="case-001",
            investigation_id="inv-001",
            segments=(
                ScriptSegment(
                    segment_id="segment-001",
                    section_id="section-001",
                    narration="Narration.",
                    claim_ids=("claim-001",),
                ),
            ),
        )

        with self.assertRaises(ValueError):
            validate_script_against_story(
                script,
                self.story,
            )

    def test_script_rejects_unverified_claim(self):
        script = Script(
            script_id="script-001",
            story_id="story-001",
            case_id="case-001",
            investigation_id="inv-001",
            segments=(
                ScriptSegment(
                    segment_id="segment-001",
                    section_id="section-001",
                    narration="Unsupported narration.",
                    claim_ids=("claim-999",),
                ),
            ),
        )

        with self.assertRaises(ValueError):
            validate_script_against_story(
                script,
                self.story,
            )

    def test_script_rejects_wrong_case(self):
        script = Script(
            script_id="script-001",
            story_id="story-001",
            case_id="case-other",
            investigation_id="inv-001",
            segments=(
                ScriptSegment(
                    segment_id="segment-001",
                    section_id="section-001",
                    narration="Narration.",
                    claim_ids=("claim-001",),
                ),
            ),
        )

        with self.assertRaises(ValueError):
            validate_script_against_story(
                script,
                self.story,
            )

    def test_script_rejects_wrong_investigation(self):
        script = Script(
            script_id="script-001",
            story_id="story-001",
            case_id="case-001",
            investigation_id="inv-other",
            segments=(
                ScriptSegment(
                    segment_id="segment-001",
                    section_id="section-001",
                    narration="Narration.",
                    claim_ids=("claim-001",),
                ),
            ),
        )

        with self.assertRaises(ValueError):
            validate_script_against_story(
                script,
                self.story,
            )


if __name__ == "__main__":
    unittest.main()
