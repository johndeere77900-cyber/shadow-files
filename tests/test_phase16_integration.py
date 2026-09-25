"""
Phase 16 qualification integration tests.

These tests verify that the qualification components work together
without modifying the operational Shadow Files workflow.
"""

from __future__ import annotations

import unittest

from app.qualification.checks import (
    check_condition,
    check_module_importable,
)
from app.qualification.models import QualificationResult
from app.qualification.report import report_summary, report_to_dict
from app.qualification.runner import QualificationRunner


class TestPhase16QualificationIntegration(unittest.TestCase):
    """Test the complete qualification infrastructure flow."""

    def test_check_to_runner_to_report_flow(self):
        def application_check():
            return check_module_importable(
                "IMPORT-001",
                "app",
            )

        def database_check():
            return check_module_importable(
                "IMPORT-002",
                "database",
            )

        def condition_check():
            return check_condition(
                "CHECK-001",
                "Qualification infrastructure",
                True,
                details="Infrastructure condition satisfied.",
            )

        runner = QualificationRunner(
            checks=(
                application_check,
                database_check,
                condition_check,
            )
        )

        report = runner.run(environment="integration")

        self.assertTrue(report.passed)
        self.assertEqual(report.total_checks, 3)
        self.assertEqual(report.passed_checks, 3)
        self.assertEqual(report.failed_checks, 0)

        summary = report_summary(report)
        self.assertIn("PASSED", summary)
        self.assertIn("3/3 checks passed", summary)

        serialized = report_to_dict(report)
        self.assertEqual(serialized["total_checks"], 3)
        self.assertEqual(serialized["passed_checks"], 3)
        self.assertTrue(serialized["passed"])

    def test_failed_check_survives_full_reporting_flow(self):
        def passing_check():
            return QualificationResult(
                check_id="CHECK-001",
                name="Passing check",
                passed=True,
            )

        def failing_check():
            return QualificationResult(
                check_id="CHECK-002",
                name="Failing check",
                passed=False,
                details="Intentional qualification failure.",
            )

        runner = QualificationRunner(
            checks=(
                passing_check,
                failing_check,
            )
        )

        report = runner.run(environment="integration")

        self.assertFalse(report.passed)
        self.assertEqual(report.total_checks, 2)
        self.assertEqual(report.passed_checks, 1)
        self.assertEqual(report.failed_checks, 1)

        summary = report_summary(report)
        self.assertIn("FAILED", summary)

        serialized = report_to_dict(report)
        self.assertFalse(serialized["passed"])
        self.assertEqual(
            serialized["results"][1]["details"],
            "Intentional qualification failure.",
        )

    def test_qualification_does_not_require_external_provider(self):
        """
        Qualification infrastructure must be executable without
        requiring live YouTube, Telegram, research, narration, or
        rendering providers.
        """
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "LOCAL-001",
                    "Local qualification execution",
                    True,
                ),
            )
        )

        report = runner.run(environment="local")

        self.assertTrue(report.passed)
        self.assertEqual(report.environment, "local")


if __name__ == "__main__":
    unittest.main()
