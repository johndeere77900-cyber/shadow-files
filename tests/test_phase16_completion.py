"""
Phase 16 completion tests.

These tests verify that the qualification infrastructure is assembled
and that the project remains compatible with the standard unittest
discovery workflow.

Passing these tests does NOT certify the complete Shadow Files system.
The final certification decision belongs to the full audit after all
implementation phases have been reviewed.
"""

from __future__ import annotations

import importlib
import unittest

from app.qualification.checks import check_condition
from app.qualification.models import QualificationReport
from app.qualification.report import report_to_dict
from app.qualification.runner import QualificationRunner


class TestPhase16Completion(unittest.TestCase):
    """Final structural checks for Phase 16."""

    def test_qualification_package_surface_is_available(self):
        modules = (
            "app.qualification",
            "app.qualification.models",
            "app.qualification.errors",
            "app.qualification.checks",
            "app.qualification.runner",
            "app.qualification.report",
        )

        for module_name in modules:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)

    def test_final_qualification_run_produces_report(self):
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "COMPLETE-001",
                    "Phase 16 infrastructure",
                    True,
                ),
                lambda: check_condition(
                    "COMPLETE-002",
                    "Unittest compatibility",
                    True,
                ),
            )
        )

        report = runner.run(
            environment="phase16-complete"
        )

        self.assertIsInstance(
            report,
            QualificationReport,
        )
        self.assertTrue(report.passed)
        self.assertEqual(report.total_checks, 2)
        self.assertEqual(report.passed_checks, 2)
        self.assertEqual(report.failed_checks, 0)

    def test_final_report_is_serializable(self):
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "COMPLETE-003",
                    "Serialization",
                    True,
                ),
            )
        )

        report = runner.run(
            environment="phase16-complete"
        )

        data = report_to_dict(report)

        self.assertIsInstance(data, dict)
        self.assertEqual(data["total_checks"], 1)
        self.assertEqual(data["passed_checks"], 1)
        self.assertEqual(data["failed_checks"], 0)
        self.assertTrue(data["passed"])

    def test_completion_infrastructure_has_no_external_provider_dependency(self):
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "COMPLETE-004",
                    "Local completion check",
                    True,
                ),
            )
        )

        report = runner.run(
            environment="local"
        )

        self.assertTrue(report.passed)

    def test_phase16_completion_does_not_equal_production_certification(self):
        """
        Phase completion only confirms that the qualification
        infrastructure itself is assembled. It does not certify the
        operational agent.
        """
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "COMPLETE-005",
                    "Scope boundary",
                    True,
                ),
            )
        )

        report = runner.run()

        self.assertTrue(report.passed)
        self.assertFalse(hasattr(report, "production_ready"))
        self.assertFalse(hasattr(report, "certified"))


if __name__ == "__main__":
    unittest.main()
