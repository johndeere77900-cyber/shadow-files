"""
Tests for Phase 16 qualification data models.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from app.qualification.models import (
    QualificationReport,
    QualificationResult,
)


class TestQualificationResult(unittest.TestCase):
    """Test QualificationResult validation."""

    def test_valid_result(self):
        result = QualificationResult(
            check_id="CHECK-001",
            name="Import test",
            passed=True,
            details="Passed.",
        )

        self.assertEqual(result.check_id, "CHECK-001")
        self.assertEqual(result.name, "Import test")
        self.assertTrue(result.passed)
        self.assertIsNotNone(result.timestamp)

    def test_empty_check_id_rejected(self):
        with self.assertRaises(ValueError):
            QualificationResult(
                check_id="",
                name="Import test",
                passed=True,
            )

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            QualificationResult(
                check_id="CHECK-001",
                name="",
                passed=True,
            )

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            QualificationResult(
                check_id="CHECK-001",
                name="Import test",
                passed=True,
                timestamp=datetime.now(),
            )


class TestQualificationReport(unittest.TestCase):
    """Test QualificationReport aggregation and validation."""

    def setUp(self):
        self.started_at = datetime.now(timezone.utc)
        self.completed_at = self.started_at + timedelta(seconds=1)

    def test_valid_report(self):
        results = (
            QualificationResult(
                check_id="CHECK-001",
                name="First check",
                passed=True,
            ),
            QualificationResult(
                check_id="CHECK-002",
                name="Second check",
                passed=True,
            ),
        )

        report = QualificationReport(
            run_id="RUN-001",
            results=results,
            started_at=self.started_at,
            completed_at=self.completed_at,
            environment="test",
        )

        self.assertEqual(report.total_checks, 2)
        self.assertEqual(report.passed_checks, 2)
        self.assertEqual(report.failed_checks, 0)
        self.assertTrue(report.passed)

    def test_failed_report(self):
        results = (
            QualificationResult(
                check_id="CHECK-001",
                name="First check",
                passed=True,
            ),
            QualificationResult(
                check_id="CHECK-002",
                name="Second check",
                passed=False,
            ),
        )

        report = QualificationReport(
            run_id="RUN-002",
            results=results,
            started_at=self.started_at,
            completed_at=self.completed_at,
        )

        self.assertEqual(report.total_checks, 2)
        self.assertEqual(report.passed_checks, 1)
        self.assertEqual(report.failed_checks, 1)
        self.assertFalse(report.passed)

    def test_empty_run_id_rejected(self):
        with self.assertRaises(ValueError):
            QualificationReport(
                run_id="",
                results=(),
                started_at=self.started_at,
                completed_at=self.completed_at,
            )

    def test_completion_before_start_rejected(self):
        with self.assertRaises(ValueError):
            QualificationReport(
                run_id="RUN-003",
                results=(),
                started_at=self.completed_at,
                completed_at=self.started_at,
            )

    def test_naive_started_at_rejected(self):
        with self.assertRaises(ValueError):
            QualificationReport(
                run_id="RUN-004",
                results=(),
                started_at=datetime.now(),
                completed_at=self.completed_at,
            )

    def test_naive_completed_at_rejected(self):
        with self.assertRaises(ValueError):
            QualificationReport(
                run_id="RUN-005",
                results=(),
                started_at=self.started_at,
                completed_at=datetime.now(),
            )


if __name__ == "__main__":
    unittest.main()
