"""
Tests for Phase 16 qualification errors.
"""

from __future__ import annotations

import unittest

from app.qualification.errors import (
    QualificationConfigurationError,
    QualificationError,
    QualificationExecutionError,
    QualificationFailure,
    QualificationReportError,
)


class TestQualificationErrors(unittest.TestCase):
    """Validate the Phase 16 qualification exception hierarchy."""

    def test_base_error_is_exception(self):
        self.assertTrue(issubclass(QualificationError, Exception))

    def test_configuration_error_inherits_base(self):
        self.assertTrue(
            issubclass(
                QualificationConfigurationError,
                QualificationError,
            )
        )

    def test_execution_error_inherits_base(self):
        self.assertTrue(
            issubclass(
                QualificationExecutionError,
                QualificationError,
            )
        )

    def test_failure_error_inherits_base(self):
        self.assertTrue(
            issubclass(
                QualificationFailure,
                QualificationError,
            )
        )

    def test_report_error_inherits_base(self):
        self.assertTrue(
            issubclass(
                QualificationReportError,
                QualificationError,
            )
        )

    def test_errors_can_be_raised_and_caught(self):
        with self.assertRaises(QualificationExecutionError):
            raise QualificationExecutionError("execution failed")

        with self.assertRaises(QualificationFailure):
            raise QualificationFailure("qualification failed")


if __name__ == "__main__":
    unittest.main()
