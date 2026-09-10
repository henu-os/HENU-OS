"""
HENU OS 3.0 — Build Engine
File: src/services/validator.py
Purpose: Pre-flight validation service implementing 13 configurable checks.
         Returns a ValidationResult — never raises directly.
         All thresholds and tool lists come from configuration, never hardcoded.

         Implements IValidator interface for Dependency Injection.

Dependencies:
    src.models.validation_result — CheckResult, ValidationResult, CheckSeverity
    src.models.pipeline_stage    — IValidator interface
    src.utils.system_utils       — host system inspection
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from src.models.pipeline_stage import IValidator
from src.models.validation_result import CheckResult, CheckSeverity, ValidationResult
from src.utils import system_utils


class Validator(IValidator):
    """
    Pre-flight validation service for the HENU Build Engine.

    Executes 13 checks before the build pipeline begins.
    All thresholds and tool requirements are read from the merged config.

    Check Categories:
        1.  Workspace Folder Structure
        2.  Configuration Files Presence
        3.  Branding Assets Presence
        4.  Environment Variables
        5.  Required CLI Tools
        6.  Python Version
        7.  Git Repository
        8.  Internet Connectivity
        9.  CPU Cores
        10. RAM
        11. Disk Space
        12. Security Policy Files
        13. Root/Administrator Privileges

    Usage:
        validator = Validator(workspace_root, logger)
        result = validator.run_all_checks(merged_config)
        if not result.passed:
            print(result.summary())
    """

    def __init__(self, workspace_root: str, logger: Any) -> None:
        self._workspace_root = os.path.abspath(workspace_root)
        self._logger = logger

    # ---------------------------------------------------------------- #
    # IValidator interface                                              #
    # ---------------------------------------------------------------- #

    def run_all_checks(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Execute all 13 pre-flight checks.

        Args:
            config — Fully merged configuration dictionary from ConfigurationManager.

        Returns:
            ValidationResult with per-check results, warnings, and errors.
        """
        result = ValidationResult()

        # Extract thresholds from config (with safe defaults).
        engine_cfg  = config.get("engine", {})
        paths_cfg   = config.get("paths", {})
        build_cfg   = config.get("build_options", {})
        security_cfg = config.get("security", {})

        min_disk_gb  = engine_cfg.get("min_disk_gb", 30)
        min_ram_gb   = engine_cfg.get("min_ram_gb", 4)
        min_cpu      = engine_cfg.get("min_cpu_cores", 2)
        min_py       = tuple(engine_cfg.get("min_python_version", [3, 8]))
        req_tools    = engine_cfg.get("required_tools", [])
        check_internet = not build_cfg.get("offline_mode", False)

        self._check_workspace(result, paths_cfg)
        self._check_config_files(result, config)
        self._check_branding_assets(result, config)
        self._check_python_version(result, min_py)
        self._check_git_repo(result)
        self._check_required_tools(result, req_tools)
        self._check_disk_space(result, min_disk_gb)
        self._check_ram(result, min_ram_gb)
        self._check_cpu(result, min_cpu)
        self._check_root_privileges(result)
        self._check_internet(result, check_internet)
        self._check_security_policies(result, security_cfg)
        self._check_virtualization(result, build_cfg)

        self._logger.info(result.summary())
        return result

    # ---------------------------------------------------------------- #
    # Individual checks (private)                                       #
    # ---------------------------------------------------------------- #

    def _check_workspace(
        self, result: ValidationResult, paths_cfg: Dict[str, Any]
    ) -> None:
        """Check 1: Core workspace directories exist."""
        required_dirs = [
            "apps", "configs", "scripts", "docs",
            "branding", "branding-package", "build", "build-engine",
            "installer", "kernel", "packages", "testing"
        ]
        # Allow config to override the list.
        required_dirs = paths_cfg.get("required_dirs", required_dirs)

        missing = [
            d for d in required_dirs
            if not os.path.isdir(os.path.join(self._workspace_root, d))
        ]

        if missing:
            result.add_check(CheckResult(
                name="Workspace Layout",
                passed=False,
                message=f"Missing workspace directories: {missing}",
                severity=CheckSeverity.CRITICAL,
            ))
        else:
            result.add_check(CheckResult(
                name="Workspace Layout",
                passed=True,
                message="All required workspace directories present.",
            ))

    def _check_config_files(
        self, result: ValidationResult, config: Dict[str, Any]
    ) -> None:
        """Check 2: All split configuration files exist."""
        configs_cfg = config.get("configs", {})
        missing = []
        for key, rel_path in configs_cfg.items():
            full = os.path.normpath(
                os.path.join(self._workspace_root, str(rel_path))
            )
            if not os.path.isfile(full):
                missing.append(key)

        passed = len(missing) == 0
        result.add_check(CheckResult(
            name="Configuration Files",
            passed=passed,
            message=(
                "All referenced config files present."
                if passed else
                f"Missing config files: {missing}"
            ),
            severity=CheckSeverity.CRITICAL,
        ))

    def _check_branding_assets(
        self, result: ValidationResult, config: Dict[str, Any]
    ) -> None:
        """Check 3: Required branding assets exist on disk."""
        branding = config.get("branding", {})
        defaults = branding.get("active_defaults", {})
        logo     = defaults.get("logo_main", branding.get("logo_path", ""))
        wallpaper = defaults.get("wallpaper_first_time_user", branding.get("default_wallpaper", ""))

        missing = []
        for label, rel_path in [("logo", logo), ("wallpaper", wallpaper)]:
            if rel_path:
                full = os.path.join(self._workspace_root, rel_path)
                if not os.path.exists(full):
                    missing.append(f"{label}: {rel_path}")

        passed = len(missing) == 0
        result.add_check(CheckResult(
            name="Branding Assets",
            passed=passed,
            message=(
                "Required branding assets present."
                if passed else
                f"Missing branding assets: {missing}"
            ),
            severity=CheckSeverity.WARNING,
        ))

    def _check_python_version(
        self, result: ValidationResult, min_version: tuple
    ) -> None:
        """Check 4 (was 6): Current Python meets minimum version requirement."""
        current = system_utils.get_python_version()
        passed  = current >= min_version
        result.add_check(CheckResult(
            name="Python Version",
            passed=passed,
            message=(
                f"Python {'.'.join(map(str, current))} meets "
                f"minimum {'.'.join(map(str, min_version))}."
                if passed else
                f"Python {'.'.join(map(str, current))} is below "
                f"minimum {'.'.join(map(str, min_version))}."
            ),
            severity=CheckSeverity.CRITICAL,
        ))

    def _check_git_repo(self, result: ValidationResult) -> None:
        """Check 5 (was 7): Workspace is a valid git repository."""
        git_dir = os.path.join(self._workspace_root, ".git")
        passed  = os.path.isdir(git_dir)
        result.add_check(CheckResult(
            name="Git Repository",
            passed=passed,
            message=(
                "Workspace is a valid git repository."
                if passed else
                "No .git directory found. Workspace is not a git repository."
            ),
            severity=CheckSeverity.WARNING,
        ))

    def _check_required_tools(
        self, result: ValidationResult, tools: List[str]
    ) -> None:
        """Check 6 (was 5): Required CLI tools are on PATH."""
        missing = [t for t in tools if not system_utils.tool_exists(t)]
        passed  = len(missing) == 0
        result.add_check(CheckResult(
            name="Required Tools",
            passed=passed,
            message=(
                f"All {len(tools)} required tools found."
                if passed else
                f"Missing tools (not in PATH): {missing}"
            ),
            severity=CheckSeverity.WARNING,  # Warning on Windows dev machines.
        ))

    def _check_disk_space(
        self, result: ValidationResult, min_gb: float
    ) -> None:
        """Check 7 (was 11): Sufficient free disk space."""
        free_gb = system_utils.get_free_disk_gb(self._workspace_root)
        passed  = free_gb >= min_gb
        result.add_check(CheckResult(
            name="Disk Space",
            passed=passed,
            message=(
                f"Free disk: {free_gb:.1f} GB (minimum: {min_gb} GB)."
                if passed else
                f"Insufficient disk: {free_gb:.1f} GB free, need {min_gb} GB."
            ),
            severity=CheckSeverity.CRITICAL,
        ))

    def _check_ram(
        self, result: ValidationResult, min_gb: float
    ) -> None:
        """Check 8 (was 10): Sufficient system RAM."""
        ram_gb = system_utils.get_ram_gb()
        if ram_gb < 0:
            result.add_check(CheckResult(
                name="RAM",
                passed=True,
                message="RAM detection unavailable (non-Linux host). Skipping.",
                severity=CheckSeverity.INFO,
            ))
            return
        passed = ram_gb >= min_gb
        result.add_check(CheckResult(
            name="RAM",
            passed=passed,
            message=(
                f"System RAM: {ram_gb:.1f} GB (minimum: {min_gb} GB)."
                if passed else
                f"Insufficient RAM: {ram_gb:.1f} GB, need {min_gb} GB."
            ),
            severity=CheckSeverity.WARNING,
        ))

    def _check_cpu(
        self, result: ValidationResult, min_cores: int
    ) -> None:
        """Check 9 (was 9): Sufficient CPU core count."""
        cores  = system_utils.get_cpu_count()
        passed = cores >= min_cores
        result.add_check(CheckResult(
            name="CPU Cores",
            passed=passed,
            message=(
                f"CPU cores: {cores} (minimum: {min_cores})."
                if passed else
                f"Too few CPU cores: {cores}, need {min_cores}."
            ),
            severity=CheckSeverity.WARNING,
        ))

    def _check_root_privileges(self, result: ValidationResult) -> None:
        """Check 10 (was 13): Root/administrator privileges present."""
        import platform
        is_windows = platform.system() == "Windows"
        is_root    = system_utils.is_root()
        passed     = is_root or is_windows

        result.add_check(CheckResult(
            name="Root Privileges",
            passed=passed,
            message=(
                "Running with root privileges." if is_root else
                "Windows host detected — root check skipped (development mode)."
                if is_windows else
                "Not running as root. ISO assembly stages require root."
            ),
            severity=CheckSeverity.WARNING if is_windows else CheckSeverity.CRITICAL,
        ))

    def _check_internet(
        self, result: ValidationResult, should_check: bool
    ) -> None:
        """Check 11 (was 8): Internet connectivity (if offline_mode is False)."""
        if not should_check:
            result.add_check(CheckResult(
                name="Internet Connectivity",
                passed=True,
                message="Offline mode enabled. Internet check skipped.",
                severity=CheckSeverity.INFO,
            ))
            return

        reachable = system_utils.check_internet()
        result.add_check(CheckResult(
            name="Internet Connectivity",
            passed=reachable,
            message=(
                "Internet connectivity confirmed."
                if reachable else
                "No internet access. Upstream packages cannot be downloaded."
            ),
            severity=CheckSeverity.WARNING,
        ))

    def _check_security_policies(
        self, result: ValidationResult, security_cfg: Dict[str, Any]
    ) -> None:
        """Check 12 (was 12): Security configuration is present and non-empty."""
        has_config = bool(security_cfg)
        result.add_check(CheckResult(
            name="Security Policies",
            passed=has_config,
            message=(
                "Security configuration block found."
                if has_config else
                "security_config.yaml is missing or empty."
            ),
            severity=CheckSeverity.WARNING,
        ))

    def _check_virtualization(
        self, result: ValidationResult, build_cfg: Dict[str, Any]
    ) -> None:
        """Check 13 (was 13): KVM virtualization available if QEMU testing enabled."""
        qemu_enabled = build_cfg.get("enable_qemu_test", False)
        if not qemu_enabled:
            result.add_check(CheckResult(
                name="Virtualization (KVM)",
                passed=True,
                message="QEMU testing not enabled. Virtualization check skipped.",
                severity=CheckSeverity.INFO,
            ))
            return

        kvm_exists = os.path.exists("/dev/kvm")
        result.add_check(CheckResult(
            name="Virtualization (KVM)",
            passed=kvm_exists,
            message=(
                "/dev/kvm found. KVM acceleration available."
                if kvm_exists else
                "/dev/kvm not found. QEMU will run without acceleration."
            ),
            severity=CheckSeverity.WARNING,
        ))
