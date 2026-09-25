"""
Tests for Phase 16 qualification checks.
"""

from __future__ import annotations

import unittest

from app.qualification.checks import (
    check_callable,
    check_condition,
    check_module_importable,
    check_modules_importable,
)
from app.qualification.models import QualificationResult


class TestQualificationChecks(unittest.TestCase):
    """Test reusable qualification checks."""

    def test_importable_module_passes(self):
        result = check_module_importable(
            "CHECK-001",
            "app",
        )

        self.assertIsInstance(result, QualificationResult)
        self.assertTrue(result.passed)

    def test_missing_module_fails(self):
        result = check_module_importable(
            "CHECK-002",
            "module_that_should_not_exist_shadow_files",
        )

        self.assertFalse(result.passed)
        self.assertIn("ModuleNotFoundError", result.details)

    def test_multiple_module_check(self):
        results = check_modules_importable(
            (
                "app",
                "database",
            )
        )

        self.assertEqual(len(results), 2)
        self.assertTrue(all(result.passed for result in results))

    def test_callable_passes(self):
        result = check_callable(
            "CHECK-003",
            "Callable check",
            lambda: None,
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.details, "Object is callable.")

    def test_non_callable_fails(self):
        result = check_callable(
            "CHECK-004",
            "Non-callable check",
            object(),
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.details, "Object is not callable.")

    def test_condition_true_passes(self):
        result = check_condition(
            "CHECK-005",
            "True condition",
            True,
            details="Condition satisfied.",
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.details, "Condition satisfied.")

    def test_condition_false_fails(self):
        result = check_condition(
            "CHECK-006",
            "False condition",
            False,
        )

        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
