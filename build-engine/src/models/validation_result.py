"""
HENU OS 3.0 — Build Engine
File: src/models/validation_result.py
Purpose: Structured data models for the validation system output.
         Returned by validator.py — never raises directly, always returns
         a ValidationResult that the pipeline interprets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class CheckSeverity(Enum):
    """Severity levels for individual pre-flight check results."""
    CRITICAL = "CRITICAL"   # Build cannot proceed if this fails.
    WARNING  = "WARNING"    # Build may proceed but issue is flagged.
    INFO     = "INFO"       # Diagnostic information only.


@dataclass
class CheckResult:
    """
    Result of a single pre-flight validation check.

    Attributes:
        name     — Human-readable check name (e.g., 'Disk Space Check').
        passed   — True if check succeeded.
        message  — Description of what was found or what failed.
        severity — How critical this check is to the build.
    """
    name: str
    passed: bool
    message: str
    severity: CheckSeverity = CheckSeverity.CRITICAL


@dataclass
class ValidationResult:
    """
    Aggregated result from running all pre-flight validation checks.

    Attributes:
        passed   — True only if all CRITICAL checks passed.
        checks   — Ordered list of individual CheckResult objects.
        warnings — Accumulated warning messages (non-fatal).
        errors   — Accumulated error messages (fatal).
    """
    passed: bool = True
    checks: List[CheckResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def add_check(self, result: CheckResult) -> None:
        """Register a CheckResult and update aggregate pass/fail state."""
        self.checks.append(result)
        if not result.passed:
            if result.severity == CheckSeverity.CRITICAL:
                self.passed = False
                self.errors.append(f"[{result.name}] {result.message}")
            elif result.severity == CheckSeverity.WARNING:
                self.warnings.append(f"[{result.name}] {result.message}")

    def summary(self) -> str:
        """Returns a human-readable pass/fail summary string."""
        total   = len(self.checks)
        passed  = sum(1 for c in self.checks if c.passed)
        failed  = total - passed
        status  = "PASSED" if self.passed else "FAILED"
        return (
            f"Validation {status}: {passed}/{total} checks passed, "
            f"{failed} failed, {len(self.warnings)} warnings."
        )
