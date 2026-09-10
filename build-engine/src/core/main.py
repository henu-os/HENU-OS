"""
HENU OS 3.0 — Build Engine
File: src/core/main.py
Purpose: CLI entry point. Parses arguments, wires all services via
         Dependency Injection, and invokes the correct command.

CLI Commands:
    henu-build build            — Execute full 14-stage pipeline.
    henu-build validate         — Run pre-flight validation only.
    henu-build clean            — Purge build artifacts and cache.
    henu-build doctor           — Full system diagnostics report.
    henu-build plugin list      — List discovered plugins.

Usage (via bootstrap_engine.py):
    python bootstrap_engine.py build
    python bootstrap_engine.py validate
    python bootstrap_engine.py doctor
"""

from __future__ import annotations

import argparse
import os
import sys
import traceback


def _resolve_workspace(engine_root: str) -> str:
    """
    The workspace root is the parent of the build-engine/ directory.
    """
    return os.path.abspath(os.path.join(engine_root, ".."))


def _build_services(workspace_root: str, profile: str, json_logs: bool):
    """
    Instantiate and wire all services.
    Returns (logger, config_manager, validator, event_bus, plugin_loader).
    """
    from src.services.logging_manager import LoggingManager
    from src.services.configuration_manager import ConfigurationManager
    from src.services.validator import Validator
    from src.services.plugin_loader import PluginLoader
    from src.core.event_bus import EventBus

    log_root = os.path.join(workspace_root, "build-engine", "logs")
    logger   = LoggingManager(log_root=log_root, json_output=json_logs)

    config_manager = ConfigurationManager(
        workspace_root=workspace_root,
        profile=profile,
    )

    validator = Validator(workspace_root=workspace_root, logger=logger)

    event_bus = EventBus()

    plugins_dir = os.path.join(workspace_root, "build-engine", "plugins")
    plugin_loader = PluginLoader(
        plugins_dir=plugins_dir,
        event_bus=event_bus,
        logger=logger,
    )

    return logger, config_manager, validator, event_bus, plugin_loader


# ------------------------------------------------------------------ #
# Command: build                                                      #
# ------------------------------------------------------------------ #

def cmd_build(args: argparse.Namespace, workspace_root: str) -> int:
    """Execute the full 14-stage build pipeline."""
    from src.core.pipeline import BuildPipeline

    logger, config_mgr, validator, event_bus, plugin_loader = _build_services(
        workspace_root, args.profile, args.json_logs
    )

    logger.info(f"HENU Build Engine starting. Profile: {args.profile}")

    # Discover plugins before pipeline starts.
    plugin_loader.discover()

    pipeline = BuildPipeline(
        workspace_root=workspace_root,
        logger=logger,
        config_manager=config_mgr,
        validator=validator,
        plugin_loader=plugin_loader,
        event_bus=event_bus,
        build_profile=args.profile,
        resume=args.resume,
    )

    try:
        context = pipeline.run()
        logger.success(f"Build complete. ID: {context.build_id}")
        return 0
    except RuntimeError as exc:
        logger.error(f"Build failed: {exc}")
        return 1


# ------------------------------------------------------------------ #
# Command: validate                                                   #
# ------------------------------------------------------------------ #

def cmd_validate(args: argparse.Namespace, workspace_root: str) -> int:
    """Run pre-flight validation checks only — do not start the build."""
    logger, config_mgr, validator, _, _ = _build_services(
        workspace_root, args.profile, args.json_logs
    )

    logger.info("Running HENU Build Engine - Validation Only")

    try:
        config_mgr.load()
        config_mgr.validate()
        config_mgr.merge()
        config_mgr.apply_overrides()
        merged = config_mgr.all()
    except Exception as exc:
        logger.error(f"Configuration load failed: {exc}")
        return 1

    result = validator.run_all_checks(merged)

    print("\n" + "=" * 60)
    print("  HENU Build Engine - Pre-Flight Validation Report")
    print("=" * 60)
    for check in result.checks:
        status = "OK" if check.passed else "--"
        print(f"  [{status}] [{check.severity.value:8s}] {check.name}: {check.message}")
    print("=" * 60)
    print(f"  {result.summary()}")
    print("=" * 60 + "\n")

    return 0 if result.passed else 1


# ------------------------------------------------------------------ #
# Command: clean                                                      #
# ------------------------------------------------------------------ #

def cmd_clean(args: argparse.Namespace, workspace_root: str) -> int:
    """Purge build artifacts, cache, and work directories."""
    from src.services.logging_manager import LoggingManager
    from src.utils.file_utils import purge_dir

    log_root = os.path.join(workspace_root, "build-engine", "logs")
    logger   = LoggingManager(log_root=log_root)

    logger.info("Cleaning build workspace...")

    targets = [
        os.path.join(workspace_root, "build", "work"),
        os.path.join(workspace_root, "build-engine", "cache", "configs"),
        os.path.join(workspace_root, "build-engine", "artifacts", "iso"),
    ]

    for path in targets:
        purge_dir(path)
        logger.info(f"Purged: {path}")

    logger.success("Clean complete.")
    return 0


# ------------------------------------------------------------------ #
# Command: verify                                                     #
# ------------------------------------------------------------------ #

def cmd_verify(args: argparse.Namespace, workspace_root: str) -> int:
    """Run comprehensive offline verification of configs, assets, and tests."""
    import unittest

    logger, config_mgr, validator, _, _ = _build_services(
        workspace_root, args.profile, args.json_logs
    )

    logger.info("Executing HENU OS 3.0 Source Integrity Verification...")

    # 1. Config & Validation Check
    try:
        config_mgr.load()
        config_mgr.validate()
        config_mgr.merge()
        config_mgr.apply_overrides()
        merged = config_mgr.all()
    except Exception as exc:
        logger.error(f"Configuration integrity check failed: {exc}")
        return 1

    val_res = validator.run_all_checks(merged)

    # 2. Run Test Suite
    test_dir = os.path.join(workspace_root, "build-engine", "tests")
    suite = unittest.defaultTestLoader.discover(test_dir)
    runner = unittest.TextTestRunner(verbosity=1)
    test_result = runner.run(suite)

    print("\n" + "=" * 60)
    print("  HENU OS 3.0 — Source Integrity Verification Report")
    print("=" * 60)
    print(f"  Configuration Check   : {'PASS' if not val_res.errors else 'FAIL'}")
    print(f"  Branding Asset Check  : {'PASS' if val_res.passed else 'PASS (Warnings)'}")
    print(f"  Unit Test Suite       : {'PASS' if test_result.wasSuccessful() else 'FAIL'} ({test_result.testsRun} tests run)")
    print("=" * 60)

    if val_res.passed and test_result.wasSuccessful():
        print("  [SUCCESS] All source integrity checks passed successfully.\n")
        return 0
    else:
        print("  [FAILURE] Verification encountered issues.\n")
        return 1


# ------------------------------------------------------------------ #
# Command: doctor                                                     #
# ------------------------------------------------------------------ #

def cmd_doctor(args: argparse.Namespace, workspace_root: str) -> int:
    """Full system diagnostics report — hardware, tools, git, Python."""
    from src.utils import system_utils

    print("\n" + "=" * 60)
    print("  HENU Build Engine — System Doctor Report")
    print("=" * 60)

    platform_info = system_utils.get_platform_info()
    for key, val in platform_info.items():
        print(f"  {key:16s}: {val}")

    print()
    py_ver = system_utils.get_python_version()
    print(f"  {'Python':16s}: {'.'.join(map(str, py_ver))}")
    print(f"  {'CPU Cores':16s}: {system_utils.get_cpu_count()}")
    print(f"  {'RAM':16s}: {system_utils.get_ram_gb():.1f} GB")
    print(f"  {'Free Disk':16s}: {system_utils.get_free_disk_gb(workspace_root):.1f} GB")
    print(f"  {'Root Privs':16s}: {system_utils.is_root()}")
    print(f"  {'Internet':16s}: {system_utils.check_internet()}")
    print(f"  {'Git Commit':16s}: {system_utils.get_git_commit(workspace_root) or 'N/A'}")

    print()
    tools = ["debootstrap", "lb", "apt-get", "dpkg", "xorriso", "git", "python3"]
    for tool in tools:
        found = system_utils.tool_exists(tool)
        tick  = "OK" if found else "--"
        print(f"  [{tick}] {tool}")

    print("=" * 60 + "\n")
    return 0


# ------------------------------------------------------------------ #
# Command: plugin list                                                #
# ------------------------------------------------------------------ #

def cmd_plugin_list(args: argparse.Namespace, workspace_root: str) -> int:
    """Discover and list all plugins with their status."""
    logger, _, _, event_bus, plugin_loader = _build_services(
        workspace_root, "development", False
    )

    plugin_loader.discover()

    plugins = plugin_loader.loaded_plugins
    print(f"\n  Discovered {len(plugins)} plugin(s):\n")
    for p in plugins:
        print(f"  • {p.name} v{p.version} by {p.author} "
              f"[priority={p.priority}] hooks={p.hooks}")
    if not plugins:
        print("  No plugins found.")
    print()
    return 0


# ------------------------------------------------------------------ #
# CLI Argument Parser                                                 #
# ------------------------------------------------------------------ #

def build_parser() -> argparse.ArgumentParser:
    """Construct the henu-build argument parser."""
    parser = argparse.ArgumentParser(
        prog="henu-build",
        description="HENU OS 3.0 — Build Engine CLI",
    )
    parser.add_argument(
        "--profile", "-p",
        choices=["development", "testing", "release", "enterprise"],
        default="development",
        help="Build profile to activate (default: development).",
    )
    parser.add_argument(
        "--json-logs",
        action="store_true",
        default=False,
        help="Output logs in JSON format for CI collectors.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # build
    build_cmd = subparsers.add_parser("build", help="Run the full build pipeline.")
    build_cmd.add_argument(
        "--resume", action="store_true",
        help="Resume from last checkpoint instead of starting fresh.",
    )

    # validate
    subparsers.add_parser("validate", help="Run pre-flight validation only.")

    # verify
    subparsers.add_parser("verify", help="Run offline source integrity verification and unit tests.")

    # clean
    subparsers.add_parser("clean", help="Purge build artifacts and cache.")

    # doctor
    subparsers.add_parser("doctor", help="System diagnostics report.")

    # plugin
    plugin_cmd = subparsers.add_parser("plugin", help="Plugin management.")
    plugin_sub = plugin_cmd.add_subparsers(dest="plugin_command", required=True)
    plugin_sub.add_parser("list", help="List all discovered plugins.")

    return parser


# ------------------------------------------------------------------ #
# Entry Point                                                         #
# ------------------------------------------------------------------ #

def main(engine_root: str) -> int:
    """
    Main entry point called by bootstrap_engine.py.

    Args:
        engine_root — Absolute path to the build-engine/ directory.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    workspace_root = _resolve_workspace(engine_root)
    parser = build_parser()
    args   = parser.parse_args()

    dispatch = {
        "build":    cmd_build,
        "validate": cmd_validate,
        "verify":   cmd_verify,
        "clean":    cmd_clean,
        "doctor":   cmd_doctor,
    }

    if args.command == "plugin":
        if args.plugin_command == "list":
            return cmd_plugin_list(args, workspace_root)
        parser.print_help()
        return 1

    handler = dispatch.get(args.command)
    if handler:
        try:
            return handler(args, workspace_root)
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            return 130
        except Exception as exc:
            print(f"\nUnexpected error: {exc}", file=sys.stderr)
            traceback.print_exc()
            return 1

    parser.print_help()
    return 1
