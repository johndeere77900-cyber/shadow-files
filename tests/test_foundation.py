"""
Shadow Files Phase 6 foundation tests.

These tests verify the foundational components before any higher-level
system is built on top of them.
"""

import unittest

from shadow_core.authorization import (
    Actor,
    AuthorizationError,
    require_role,
)

from shadow_core.audit import new_audit_event

from shadow_core.config import Config

from shadow_core.jobs import create_job

from shadow_core.retry import (
    RetryPolicy,
    should_retry,
)

from shadow_core.states import (
    CaseState,
    InvalidTransition,
    transition,
)


class FoundationTests(unittest.TestCase):

    def test_valid_state_transition(self):
        result = transition(
            CaseState.IDEA,
            CaseState.CASE_SELECTED,
        )

        self.assertEqual(
            result,
            CaseState.CASE_SELECTED,
        )

    def test_invalid_state_transition_is_rejected(self):
        with self.assertRaises(InvalidTransition):
            transition(
                CaseState.IDEA,
                CaseState.PUBLISHED,
            )

    def test_audit_event_has_unique_id_and_timestamp(self):
        event = new_audit_event(
            actor="system",
            intent="foundation_test",
            command="test_audit",
            target="case:test",
            result="SUCCESS",
        )

        self.assertTrue(event.event_id)
        self.assertTrue(event.timestamp)
        self.assertEqual(event.result, "SUCCESS")

    def test_audit_event_is_immutable(self):
        event = new_audit_event(
            actor="system",
            intent="foundation_test",
            command="test_audit",
            target="case:test",
            result="SUCCESS",
        )

        with self.assertRaises(AttributeError):
            event.result = "FAILED"

    def test_jobs_have_unique_ids(self):
        job_one = create_job("foundation_test")
        job_two = create_job("foundation_test")

        self.assertNotEqual(
            job_one.job_id,
            job_two.job_id,
        )

    def test_empty_job_operation_is_rejected(self):
        with self.assertRaises(ValueError):
            create_job("")

    def test_authorized_role_is_accepted(self):
        actor = Actor(
            actor_id="boss",
            role="owner",
        )

        require_role(
            actor,
            "owner",
        )

    def test_unauthorized_role_is_rejected(self):
        actor = Actor(
            actor_id="test-user",
            role="viewer",
        )

        with self.assertRaises(AuthorizationError):
            require_role(
                actor,
                "owner",
            )

    def test_default_configuration(self):
        config = Config.from_env()

        self.assertEqual(
            config.app_name,
            "Shadow Files",
        )

        self.assertFalse(
            config.youtube_enabled,
        )

    def test_retry_policy_allows_remaining_attempts(self):
        policy = RetryPolicy(
            max_attempts=3,
        )

        self.assertTrue(
            should_retry(
                0,
                policy,
            )
        )

        self.assertTrue(
            should_retry(
                1,
                policy,
            )
        )

        self.assertTrue(
            should_retry(
                2,
                policy,
            )
        )

        self.assertFalse(
            should_retry(
                3,
                policy,
            )
        )

    def test_retry_policy_rejects_invalid_attempt(self):
        policy = RetryPolicy(
            max_attempts=3,
        )

        with self.assertRaises(ValueError):
            should_retry(
                -1,
                policy,
            )


if __name__ == "__main__":
    unittest.main()
