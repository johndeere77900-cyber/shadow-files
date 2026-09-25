"""
Shadow Files Phase 12 investigation model tests.

These tests verify validation and immutability of the core
investigation objects.
"""

import unittest
from datetime import datetime, timezone

from app.investigation.models import (
    Investigation,
    ResearchItem,
    ResearchItemType,
    ResearchStatus,
)
from app.investigation.sources import (
    ResearchSource,
    SourceValidationError,
    create_research_source,
)
from app.investigation.timeline import TimelineEvent


class InvestigationModelTests(unittest.TestCase):
    """Validate investigation models."""

    def setUp(self) -> None:
        self.now = datetime.now(timezone.utc)

    def test_investigation_accepts_valid_record(self) -> None:
        investigation = Investigation(
            investigation_id="INV-001",
            case_id="CASE-001",
            status=ResearchStatus.NOT_STARTED,
            started_at=self.now,
        )

        self.assertEqual(
            investigation.investigation_id,
            "INV-001",
        )
        self.assertEqual(
            investigation.status,
            ResearchStatus.NOT_STARTED,
        )

    def test_investigation_requires_id(self) -> None:
        with self.assertRaises(ValueError):
            Investigation(
                investigation_id="",
                case_id="CASE-001",
                status=ResearchStatus.NOT_STARTED,
                started_at=self.now,
            )

    def test_investigation_requires_case(self) -> None:
        with self.assertRaises(ValueError):
            Investigation(
                investigation_id="INV-001",
                case_id="",
                status=ResearchStatus.NOT_STARTED,
                started_at=self.now,
            )

    def test_investigation_rejects_naive_timestamp(self) -> None:
        with self.assertRaises(ValueError):
            Investigation(
                investigation_id="INV-001",
                case_id="CASE-001",
                status=ResearchStatus.NOT_STARTED,
                started_at=datetime.now(),
            )

    def test_investigation_is_immutable(self) -> None:
        investigation = Investigation(
            investigation_id="INV-001",
            case_id="CASE-001",
            status=ResearchStatus.NOT_STARTED,
            started_at=self.now,
        )

        with self.assertRaises(AttributeError):
            investigation.status = ResearchStatus.RESEARCHING

    def test_research_item_accepts_valid_record(self) -> None:
        item = ResearchItem(
            item_id="ITEM-001",
            investigation_id="INV-001",
            item_type=ResearchItemType.FACT,
            statement="A documented event occurred.",
            discovered_at=self.now,
        )

        self.assertEqual(
            item.item_type,
            ResearchItemType.FACT,
        )

    def test_research_item_requires_statement(self) -> None:
        with self.assertRaises(ValueError):
            ResearchItem(
                item_id="ITEM-001",
                investigation_id="INV-001",
                item_type=ResearchItemType.FACT,
                statement="",
                discovered_at=self.now,
            )

    def test_research_item_is_immutable(self) -> None:
        item = ResearchItem(
            item_id="ITEM-001",
            investigation_id="INV-001",
            item_type=ResearchItemType.FACT,
            statement="A documented event occurred.",
            discovered_at=self.now,
        )

        with self.assertRaises(AttributeError):
            item.statement = "Changed."

    def test_source_factory_normalizes_text(self) -> None:
        source = create_research_source(
            source_id=" SOURCE-001 ",
            investigation_id=" INV-001 ",
            name=" Example Source ",
            url=" https://example.com ",
            publisher=" Example Publisher ",
            discovered_at=self.now,
        )

        self.assertEqual(source.source_id, "SOURCE-001")
        self.assertEqual(source.investigation_id, "INV-001")
        self.assertEqual(source.name, "Example Source")
        self.assertEqual(source.url, "https://example.com")
        self.assertEqual(
            source.publisher,
            "Example Publisher",
        )

    def test_source_requires_name(self) -> None:
        with self.assertRaises(SourceValidationError):
            create_research_source(
                source_id="SOURCE-001",
                investigation_id="INV-001",
                name="",
                url=None,
                publisher=None,
                discovered_at=self.now,
            )

    def test_source_is_immutable(self) -> None:
        source = ResearchSource(
            source_id="SOURCE-001",
            investigation_id="INV-001",
            name="Example Source",
            url=None,
            publisher=None,
            discovered_at=self.now,
        )

        with self.assertRaises(AttributeError):
            source.name = "Changed Source"

    def test_timeline_event_accepts_valid_record(self) -> None:
        event = TimelineEvent(
            event_id="EVENT-001",
            investigation_id="INV-001",
            event_date=self.now,
            description="A documented event.",
        )

        self.assertEqual(
            event.event_id,
            "EVENT-001",
        )

    def test_timeline_event_requires_description(self) -> None:
        with self.assertRaises(ValueError):
            TimelineEvent(
                event_id="EVENT-001",
                investigation_id="INV-001",
                event_date=self.now,
                description="",
            )

    def test_timeline_event_is_immutable(self) -> None:
        event = TimelineEvent(
            event_id="EVENT-001",
            investigation_id="INV-001",
            event_date=self.now,
            description="A documented event.",
        )

        with self.assertRaises(AttributeError):
            event.description = "Changed."


if __name__ == "__main__":
    unittest.main()
