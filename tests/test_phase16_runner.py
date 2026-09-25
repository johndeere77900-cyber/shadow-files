"""
Tests for the Phase 16 qualification runner.
"""

from __future__ import annotations

import unittest

from app.qualification.errors import QualificationExecutionError
from app.qualification.models import QualificationResult
from app.qualification.runner import QualificationRunner


class TestQualificationRunner(unittest.TestCase):
    """Test qualification check execution."""

    def test_runner_executes_registered_checks(self):
        def check_one():
            return QualificationResult(
                check_id="CHECK-001",
                name="First",
                passed=True,
            )

        def check_two():
            return QualificationResult(
                check_id="CHECK-002",
                name="Second",
                passed=True,
            )

        runner = QualificationRunner(
            checks=(check_one, check_two)
        )

        report = runner.run(environment="test")

        self.assertEqual(report.total_checks, 2)
        self.assertEqual(report.passed_checks, 2)
        self.assertEqual(report.failed_checks, 0)
        self.assertTrue(report.passed)
        self.assertEqual(report.environment, "test")

    def test_runner_preserves_failed_check(self):
        def failed_check():
            return QualificationResult(
                check_id="CHECK-003",
                name="Failed check",
                passed=False,
                details="Expected failure.",
            )

        runner = QualificationRunner(checks=(failed_check,))

        report = runner.run()

        self.assertEqual(report.total_checks, 1)
        self.assertEqual(report.passed_checks, 0)
        self.assertEqual(report.failed_checks, 1)
        self.assertFalse(report.passed)

    def test_runner_rejects_invalid_check_result(self):
        def invalid_check():
            return "not a qualification result"

        runner = QualificationRunner(checks=(invalid_check,))

        with self.assertRaises(QualificationExecutionError):
            runner.run()

    def test_runner_wraps_check_exception(self):
        def broken_check():
            raise RuntimeError("boom")

        runner = QualificationRunner(checks=(broken_check,))

        with self.assertRaises(QualificationExecutionError) as context:
            runner.run()

        self.assertIn("boom", str(context.exception))

    def test_empty_runner_produces_unpassed_report(self):
        runner = QualificationRunner()

        report = runner.run()

        self.assertEqual(report.total_checks, 0)
        self.assertEqual(report.passed_checks, 0)
        self.assertEqual(report.failed_checks, 0)
        self.assertFalse(report.passed)

    def test_checks_property_is_immutable_tuple(self):
        runner = QualificationRunner()

        self.assertIsInstance(runner.checks, tuple)
        self.assertEqual(runner.checks, ())


if __name__ == "__main__":
    unittest.main()
