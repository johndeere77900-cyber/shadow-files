"""
Final infrastructure checks for Phase 16 qualification.

This file verifies that the complete qualification layer is assembled
and usable before the final whole-system audit.
"""

from __future__ import annotations

import importlib
import unittest

from app.qualification.checks import check_condition
from app.qualification.report import report_summary
from app.qualification.runner import QualificationRunner


class TestPhase16FinalInfrastructure(unittest.TestCase):
    """Validate the assembled Phase 16 qualification infrastructure."""

    def test_all_qualification_components_import(self):
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

    def test_runner_can_execute_final_infrastructure_check(self):
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "FINAL-001",
                    "Qualification infrastructure assembled",
                    True,
                    details="Phase 16 qualification components are operational.",
                ),
            )
        )

        report = runner.run(
            environment="phase16-final-infrastructure"
        )

        self.assertTrue(report.passed)
        self.assertEqual(report.total_checks, 1)
        self.assertEqual(report.passed_checks, 1)
        self.assertEqual(report.failed_checks, 0)

    def test_final_summary_reports_success(self):
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "FINAL-002",
                    "Final summary check",
                    True,
                ),
            )
        )

        report = runner.run(
            environment="phase16-final-infrastructure"
        )

        summary = report_summary(report)

        self.assertIn("PASSED", summary)
        self.assertIn("1/1 checks passed", summary)

    def test_final_infrastructure_does_not_claim_production_readiness(self):
        """
        The qualification infrastructure reports test results only.
        It must not expose a field that silently represents production
        certification.
        """
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "FINAL-003",
                    "Scope boundary",
                    True,
                ),
            )
        )

        report = runner.run()

        self.assertTrue(report.passed)
        self.assertFalse(
            hasattr(report, "production_ready")
        )
        self.assertFalse(
            hasattr(report, "certified")
        )


if __name__ == "__main__":
    unittest.main()
