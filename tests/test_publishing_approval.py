"""
Tests for Shadow Files publication approval controls.
"""

import unittest
from datetime import datetime, timezone

from app.publishing.approval import (
    create_approval_record,
    require_approved_publication,
    validate_approval,
)
from app.publishing.errors import PublicationApprovalError
from app.publishing.models import (
    Publication,
    PublicationMode,
    PublicationPackage,
)
from app.publishing.status import PublicationStatus


class TestPublicationApproval(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)

        self.package = PublicationPackage(
            production_id="prod-001",
            video_location="/videos/episode.mp4",
            thumbnail_location="/images/thumbnail.jpg",
            title="Shadow Files Episode",
            description="A completed episode.",
        )

    def make_publication(
        self,
        status: PublicationStatus,
    ) -> Publication:
        return Publication(
            publication_id="pub-001",
            production_id="prod-001",
            mode=PublicationMode.HUMAN,
            status=status,
            package=self.package,
            created_at=self.now,
            updated_at=self.now,
        )

    def test_pending_approval_can_be_validated(self):
        publication = self.make_publication(
            PublicationStatus.PENDING_APPROVAL
        )

        validate_approval(publication)

    def test_paused_publication_can_be_validated(self):
        publication = self.make_publication(
            PublicationStatus.PAUSED
        )

        validate_approval(publication)

    def test_not_started_cannot_be_approved(self):
        publication = self.make_publication(
            PublicationStatus.NOT_STARTED
        )

        with self.assertRaises(PublicationApprovalError):
            validate_approval(publication)

    def test_approved_record_is_created(self):
        publication = self.make_publication(
            PublicationStatus.PENDING_APPROVAL
        )

        record = create_approval_record(
            publication,
            approved_by="Boss",
            note="Final review completed.",
        )

        self.assertEqual(
            record.publication_id,
            "pub-001",
        )
        self.assertTrue(record.approved)
        self.assertEqual(
            record.approved_by,
            "Boss",
        )
        self.assertEqual(
            record.note,
            "Final review completed.",
        )
        self.assertIsNotNone(record.approved_at)
        self.assertIsNotNone(record.approved_at.tzinfo)

    def test_empty_approver_is_rejected(self):
        publication = self.make_publication(
            PublicationStatus.PENDING_APPROVAL
        )

        with self.assertRaises(PublicationApprovalError):
            create_approval_record(
                publication,
                approved_by="",
            )

    def test_approved_status_passes_requirement(self):
        publication = self.make_publication(
            PublicationStatus.APPROVED
        )

        require_approved_publication(publication)

    def test_non_approved_status_fails_requirement(self):
        publication = self.make_publication(
            PublicationStatus.PENDING_APPROVAL
        )

        with self.assertRaises(PublicationApprovalError):
            require_approved_publication(publication)

    def test_uploading_status_fails_requirement(self):
        publication = self.make_publication(
            PublicationStatus.UPLOADING
        )

        with self.assertRaises(PublicationApprovalError):
            require_approved_publication(publication)


if __name__ == "__main__":
    unittest.main()
