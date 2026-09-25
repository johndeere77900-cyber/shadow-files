"""
Phase 16 qualification contract tests.

These tests verify stable behavioral contracts for the qualification
infrastructure without making assumptions about external services.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.qualification.checks import (
    check_callable,
    check_condition,
    check_module_importable,
)
from app.qualification.models import (
    QualificationReport,
    QualificationResult,
)
from app.qualification.report import report_to_dict
from app.qualification.runner import QualificationRunner


class TestPhase16Contracts(unittest.TestCase):
    """Validate stable qualification infrastructure contracts."""

    def test_result_is_frozen(self):
        result = QualificationResult(
            check_id="CONTRACT-001",
            name="Frozen result",
            passed=True,
        )

        with self.assertRaises(AttributeError):
            result.passed = False

    def test_report_is_frozen(self):
        now = datetime.now(timezone.utc)

        report = QualificationReport(
            run_id="CONTRACT-RUN-001",
            results=(),
            started_at=now,
            completed_at=now,
        )

        with self.assertRaises(AttributeError):
            report.run_id = "changed"

    def test_result_timestamp_is_timezone_aware(self):
        result = QualificationResult(
            check_id="CONTRACT-002",
            name="Timestamp",
            passed=True,
        )

        self.assertIsNotNone(result.timestamp.tzinfo)
        self.assertIsNotNone(result.timestamp.utcoffset())

    def test_check_helpers_return_results(self):
        results = (
            check_condition(
                "CONTRACT-003",
                "Condition",
                True,
            ),
            check_callable(
                "CONTRACT-004",
                "Callable",
                lambda: None,
            ),
            check_module_importable(
                "CONTRACT-005",
                "app",
            ),
        )

        self.assertTrue(
            all(
                isinstance(result, QualificationResult)
                for result in results
            )
        )
        self.assertTrue(
            all(result.passed for result in results)
        )

    def test_runner_returns_report(self):
        runner = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "CONTRACT-006",
                    "Runner contract",
                    True,
                ),
            )
        )

        report = runner.run()

        self.assertIsInstance(report, QualificationReport)

    def test_serialized_report_has_expected_top_level_keys(self):
        report = QualificationRunner(
            checks=(
                lambda: check_condition(
                    "CONTRACT-007",
                    "Serialization contract",
                    True,
                ),
            )
        ).run()

        data = report_to_dict(report)

        expected_keys = {
            "run_id",
            "environment",
            "started_at",
            "completed_at",
            "total_checks",
            "passed_checks",
            "failed_checks",
            "passed",
            "results",
        }

        self.assertEqual(
            set(data.keys()),
            expected_keys,
        )


if __name__ == "__main__":
    unittest.main()
