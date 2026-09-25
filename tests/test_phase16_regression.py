"""
Phase 16 regression tests.

These tests protect the qualification infrastructure against accidental
regressions while the final system is being completed.
"""

from __future__ import annotations

import importlib
import unittest

from app.qualification.checks import check_condition
from app.qualification.models import QualificationResult
from app.qualification.report import report_to_dict
from app.qualification.runner import QualificationRunner


class TestPhase16Regression(unittest.TestCase):
    """Regression checks for previously established behavior."""

    def test_qualification_modules_remain_importable(self):
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

    def test_result_creation_remains_stable(self):
        result = QualificationResult(
            check_id="REG-001",
            name="Regression result",
            passed=True,
            details="Stable behavior.",
        )

        self.assertEqual(result.check_id, "REG-001")
        self.assertEqual(result.name, "Regression result")
        self.assertTrue(result.passed)
        self.assertEqual(result.details, "Stable behavior.")

    def test_runner_preserves_check_order(self):
        executed: list[str] = []

        def first():
            executed.append("first")
            return check_condition(
                "REG-002",
                "First",
                True,
            )

        def second():
            executed.append("second")
            return check_condition(
                "REG-003",
                "Second",
                True,
            )

        def third():
            executed.append("third")
            return check_condition(
                "REG-004",
                "Third",
                True,
            )

        report = QualificationRunner(
            checks=(first, second, third)
        ).run()

        self.assertTrue(report.passed)
        self.assertEqual(
            executed,
            ["first", "second", "third"],
        )

    def test_failed_result_remains_visible_in_serialized_report(self):
        report = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "REG-005",
                    "Intentional failure",
                    False,
                    details="Regression failure marker.",
                ),
            )
        ).run()

        data = report_to_dict(report)

        self.assertFalse(data["passed"])
        self.assertEqual(data["failed_checks"], 1)
        self.assertEqual(
            data["results"][0]["details"],
            "Regression failure marker.",
        )

    def test_runner_does_not_silently_convert_failed_checks_to_pass(self):
        report = QualificationRunner(
            checks=(
                lambda: QualificationResult(
                    check_id="REG-006",
                    name="Explicit failure",
                    passed=False,
                ),
            )
        ).run()

        self.assertFalse(report.passed)
        self.assertEqual(report.passed_checks, 0)
        self.assertEqual(report.failed_checks, 1)


if __name__ == "__main__":
    unittest.main()
