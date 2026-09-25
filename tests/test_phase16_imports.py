"""
Phase 16 repository-wide import qualification tests.

These tests verify that the major application packages required by
Shadow Files remain importable together.
"""

from __future__ import annotations

import importlib
import unittest


class TestPhase16Imports(unittest.TestCase):
    """Validate the currently established application package surface."""

    def test_application_packages_import(self):
        modules = (
            "app",
            "app.cases",
            "app.evidence",
            "app.investigation",
            "app.production",
            "app.scheduler",
            "app.publishing",
            "app.qualification",
        )

        for module_name in modules:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)

    def test_database_package_imports(self):
        module = importlib.import_module("database")
        self.assertIsNotNone(module)

    def test_qualification_modules_import(self):
        modules = (
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

    def test_publishing_modules_import(self):
        modules = (
            "app.publishing.models",
            "app.publishing.status",
            "app.publishing.repository",
            "app.publishing.service",
            "app.publishing.youtube",
        )

        for module_name in modules:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)


if __name__ == "__main__":
    unittest.main()
