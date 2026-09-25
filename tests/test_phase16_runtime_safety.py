"""
Phase 16 runtime-safety qualification tests.

These checks verify that qualification infrastructure can be imported
and executed without requiring live external services.
"""

from __future__ import annotations

import unittest

from app.qualification.checks import check_condition
from app.qualification.models import QualificationResult
from app.qualification.runner import QualificationRunner


class TestPhase16RuntimeSafety(unittest.TestCase):
    """Validate local execution safety of qualification infrastructure."""

    def test_qualification_runner_is_local(self):
        def local_check():
            return check_condition(
                "LOCAL-001",
                "Local execution",
                True,
            )

        report = QualificationRunner(
            checks=(local_check,)
        ).run(environment="qualification-test")

        self.assertTrue(report.passed)
        self.assertEqual(report.total_checks, 1)

    def test_check_result_is_structured(self):
        result = check_condition(
            "STRUCT-001",
            "Structured result",
            True,
        )

        self.assertIsInstance(result, QualificationResult)
        self.assertEqual(result.check_id, "STRUCT-001")
        self.assertTrue(result.passed)

    def test_failed_condition_does_not_raise(self):
        result = check_condition(
            "STRUCT-002",
            "Expected failed condition",
            False,
            details="Expected qualification failure.",
        )

        self.assertIsInstance(result, QualificationResult)
        self.assertFalse(result.passed)

    def test_multiple_local_checks_execute_in_order(self):
        execution_order: list[str] = []

        def first_check():
            execution_order.append("first")
            return check_condition(
                "ORDER-001",
                "First check",
                True,
            )

        def second_check():
            execution_order.append("second")
            return check_condition(
                "ORDER-002",
                "Second check",
                True,
            )

        runner = QualificationRunner(
            checks=(first_check, second_check)
        )

        report = runner.run(environment="qualification-test")

        self.assertTrue(report.passed)
        self.assertEqual(
            execution_order,
            ["first", "second"],
        )

    def test_no_external_provider_is_required(self):
        """
        The qualification runner itself must not require a live
        external provider simply to execute local checks.
        """
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "LOCAL-002",
                    "External-provider independence",
                    True,
                ),
            )
        )

        report = runner.run()

        self.assertTrue(report.passed)


if __name__ == "__main__":
    unittest.main()
