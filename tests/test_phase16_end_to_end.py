"""
Phase 16 end-to-end qualification tests.

These tests exercise the qualification infrastructure as a complete
local workflow: checks -> runner -> report -> serialized report.
"""

from __future__ import annotations

import unittest

from app.qualification.checks import (
    check_condition,
    check_module_importable,
)
from app.qualification.report import report_summary, report_to_dict
from app.qualification.runner import QualificationRunner


class TestPhase16EndToEnd(unittest.TestCase):
    """Validate the complete local qualification workflow."""

    def test_complete_successful_workflow(self):
        checks = (
            lambda: check_module_importable(
                "E2E-001",
                "app",
            ),
            lambda: check_module_importable(
                "E2E-002",
                "database",
            ),
            lambda: check_condition(
                "E2E-003",
                "Qualification infrastructure",
                True,
                details="Local qualification infrastructure is operational.",
            ),
        )

        runner = QualificationRunner(checks=checks)
        report = runner.run(environment="end-to-end")

        self.assertTrue(report.passed)
        self.assertEqual(report.total_checks, 3)
        self.assertEqual(report.passed_checks, 3)
        self.assertEqual(report.failed_checks, 0)

        summary = report_summary(report)
        self.assertIn("PASSED", summary)

        data = report_to_dict(report)
        self.assertTrue(data["passed"])
        self.assertEqual(data["total_checks"], 3)
        self.assertEqual(data["passed_checks"], 3)

    def test_complete_failed_workflow_is_reported(self):
        checks = (
            lambda: check_condition(
                "E2E-004",
                "Passing prerequisite",
                True,
            ),
            lambda: check_condition(
                "E2E-005",
                "Failed prerequisite",
                False,
                details="Intentional failure for qualification testing.",
            ),
        )

        report = QualificationRunner(
            checks=checks
        ).run(environment="end-to-end")

        self.assertFalse(report.passed)
        self.assertEqual(report.total_checks, 2)
        self.assertEqual(report.passed_checks, 1)
        self.assertEqual(report.failed_checks, 1)

        data = report_to_dict(report)

        self.assertFalse(data["passed"])
        self.assertEqual(data["failed_checks"], 1)

    def test_report_contains_every_executed_check(self):
        checks = tuple(
            (
                lambda index=index: check_condition(
                    f"E2E-{index:03d}",
                    f"Check {index}",
                    True,
                )
            )
            for index in range(1, 6)
        )

        report = QualificationRunner(
            checks=checks
        ).run(environment="end-to-end")

        self.assertEqual(report.total_checks, 5)

        check_ids = [
            result.check_id
            for result in report.results
        ]

        self.assertEqual(
            check_ids,
            [
                "E2E-001",
                "E2E-002",
                "E2E-003",
                "E2E-004",
                "E2E-005",
            ],
        )

    def test_environment_is_preserved(self):
        report = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "E2E-006",
                    "Environment check",
                    True,
                ),
            )
        ).run(environment="final-qualification")

        self.assertEqual(
            report.environment,
            "final-qualification",
        )


if __name__ == "__main__":
    unittest.main()
