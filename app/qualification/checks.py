"""
Reusable qualification checks for the final Shadow Files audit.

These checks are intentionally lightweight and deterministic. They
validate structural/runtime conditions without making claims about
external providers or production readiness by themselves.
"""

from __future__ import annotations

import importlib
from collections.abc import Iterable

from app.qualification.models import QualificationResult


def check_module_importable(
    check_id: str,
    module_name: str,
) -> QualificationResult:
    """Check whether a Python module can be imported."""
    try:
        importlib.import_module(module_name)
    except Exception as exc:
        return QualificationResult(
            check_id=check_id,
            name=f"Import {module_name}",
            passed=False,
            details=f"{type(exc).__name__}: {exc}",
        )

    return QualificationResult(
        check_id=check_id,
        name=f"Import {module_name}",
        passed=True,
        details="Module imported successfully.",
    )


def check_modules_importable(
    modules: Iterable[str],
    *,
    prefix: str = "IMPORT",
) -> tuple[QualificationResult, ...]:
    """Run import checks for a collection of module names."""
    results: list[QualificationResult] = []

    for index, module_name in enumerate(modules, start=1):
        results.append(
            check_module_importable(
                f"{prefix}-{index:03d}",
                module_name,
            )
        )

    return tuple(results)


def check_callable(
    check_id: str,
    name: str,
    value: object,
) -> QualificationResult:
    """Check whether a supplied object is callable."""
    passed = callable(value)

    return QualificationResult(
        check_id=check_id,
        name=name,
        passed=passed,
        details=(
            "Object is callable."
            if passed
            else "Object is not callable."
        ),
    )


def check_condition(
    check_id: str,
    name: str,
    condition: bool,
    *,
    details: str = "",
) -> QualificationResult:
    """Create a qualification result from a boolean condition."""
    return QualificationResult(
        check_id=check_id,
        name=name,
        passed=bool(condition),
        details=details,
  )
