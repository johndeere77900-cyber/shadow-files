"""
Tests for Shadow Files publication status transitions.
"""

import unittest

from app.publishing.status import (
    ALLOWED_TRANSITIONS,
    PublicationStatus,
    can_transition,
    validate_transition,
)


class TestPublicationStatus(unittest.TestCase):
    def test_all_statuses_are_defined(self):
        expected = {
            "NOT_STARTED",
            "PACKAGE_READY",
            "PENDING_APPROVAL",
            "APPROVED",
            "UPLOADING",
            "UPLOADED",
            "SCHEDULED",
            "PUBLISHED",
            "BLOCKED",
            "FAILED",
            "PAUSED",
            "CANCELLED",
        }

        actual = {
            status.value
            for status in PublicationStatus
        }

        self.assertEqual(actual, expected)

    def test_valid_happy_path_transitions(self):
        path = [
            PublicationStatus.NOT_STARTED,
            PublicationStatus.PACKAGE_READY,
            PublicationStatus.PENDING_APPROVAL,
            PublicationStatus.APPROVED,
            PublicationStatus.UPLOADING,
            PublicationStatus.UPLOADED,
            PublicationStatus.SCHEDULED,
            PublicationStatus.PUBLISHED,
        ]

        for current, target in zip(path, path[1:]):
            self.assertTrue(
                can_transition(current, target),
                f"{current} -> {target} should be valid",
            )

    def test_uploaded_can_become_published_directly(self):
        self.assertTrue(
            can_transition(
                PublicationStatus.UPLOADED,
                PublicationStatus.PUBLISHED,
            )
        )

    def test_invalid_transition_is_rejected(self):
        self.assertFalse(
            can_transition(
                PublicationStatus.NOT_STARTED,
                PublicationStatus.PUBLISHED,
            )
        )

    def test_approved_cannot_skip_to_published(self):
        self.assertFalse(
            can_transition(
                PublicationStatus.APPROVED,
                PublicationStatus.PUBLISHED,
            )
        )

    def test_published_is_terminal(self):
        self.assertEqual(
            ALLOWED_TRANSITIONS[PublicationStatus.PUBLISHED],
            set(),
        )

    def test_cancelled_is_terminal(self):
        self.assertEqual(
            ALLOWED_TRANSITIONS[PublicationStatus.CANCELLED],
            set(),
        )

    def test_invalid_transition_raises(self):
        with self.assertRaises(ValueError):
            validate_transition(
                PublicationStatus.NOT_STARTED,
                PublicationStatus.PUBLISHED,
            )

    def test_valid_transition_does_not_raise(self):
        validate_transition(
            PublicationStatus.NOT_STARTED,
            PublicationStatus.PACKAGE_READY,
        )

    def test_failed_can_be_recovered_to_package_ready(self):
        self.assertTrue(
            can_transition(
                PublicationStatus.FAILED,
                PublicationStatus.PACKAGE_READY,
            )
        )

    def test_blocked_can_be_recovered_to_package_ready(self):
        self.assertTrue(
            can_transition(
                PublicationStatus.BLOCKED,
                PublicationStatus.PACKAGE_READY,
            )
        )

    def test_approval_is_required_before_upload(self):
        self.assertFalse(
            can_transition(
                PublicationStatus.PENDING_APPROVAL,
                PublicationStatus.UPLOADING,
            )
        )

        self.assertTrue(
            can_transition(
                PublicationStatus.PENDING_APPROVAL,
                PublicationStatus.APPROVED,
            )
        )


if __name__ == "__main__":
    unittest.main()
