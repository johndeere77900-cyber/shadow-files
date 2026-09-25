"""
Tests for Phase 16 qualification report utilities.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.qualification.models import QualificationReport, QualificationResult
from app.qualification.report import report_summary, report_to_dict


class TestQualificationReportUtilities(unittest.TestCase):
    """Test qualification report formatting and serialization."""

    def setUp(self):
        started_at = datetime.now(timezone.utc)
        completed_at = datetime.now(timezone.utc)

        self.report = QualificationReport(
            run_id="RUN-001",
            results=(
                QualificationResult(
                    check_id="CHECK-001",
                    name="First check",
                    passed=True,
                    details="Passed.",
                ),
                QualificationResult(
                    check_id="CHECK-002",
                    name="Second check",
                    passed=False,
                    details="Failed.",
                ),
            ),
            started_at=started_at,
            completed_at=completed_at,
            environment="test",
        )

    def test_report_summary_contains_status(self):
        summary = report_summary(self.report)

        self.assertIn("FAILED", summary)
        self.assertIn("1/2", summary)
        self.assertIn("1 failed", summary)

    def test_report_to_dict_contains_run_metadata(self):
        data = report_to_dict(self.report)

        self.assertEqual(data["run_id"], "RUN-001")
        self.assertEqual(data["environment"], "test")
        self.assertEqual(data["total_checks"], 2)
        self.assertEqual(data["passed_checks"], 1)
        self.assertEqual(data["failed_checks"], 1)
        self.assertFalse(data["passed"])

    def test_report_to_dict_contains_results(self):
        data = report_to_dict(self.report)

        self.assertEqual(len(data["results"]), 2)

        first = data["results"][0]
        self.assertEqual(first["check_id"], "CHECK-001")
        self.assertEqual(first["name"], "First check")
        self.assertTrue(first["passed"])
        self.assertEqual(first["details"], "Passed.")

        second = data["results"][1]
        self.assertEqual(second["check_id"], "CHECK-002")
        self.assertFalse(second["passed"])

    def test_report_timestamps_are_serialized(self):
        data = report_to_dict(self.report)

        self.assertIsInstance(data["started_at"], str)
        self.assertIsInstance(data["completed_at"], str)

        self.assertTrue(data["started_at"])
        self.assertTrue(data["completed_at"])

    def test_passing_report_summary(self):
        report = QualificationReport(
            run_id="RUN-002",
            results=(
                QualificationResult(
                    check_id="CHECK-003",
                    name="Successful check",
                    passed=True,
                ),
            ),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        summary = report_summary(report)

        self.assertIn("PASSED", summary)
        self.assertIn("1/1", summary)
        self.assertIn("0 failed", summary)


if __name__ == "__main__":
    unittest.main()
