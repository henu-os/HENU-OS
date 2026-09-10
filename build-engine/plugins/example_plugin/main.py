"""
HENU OS 3.0 — Build Engine
File: build-engine/plugins/example_plugin/main.py
Purpose: Reference implementation of a HENU Build Engine plugin.
         Demonstrates all 6 lifecycle hooks and correct BuildContext usage.
         This plugin is DISABLED by default (enabled: false in plugin.yaml).

Lifecycle Hooks Implemented:
    initialize()     — Runs after plugin is loaded, before pipeline.
    before_build()   — Runs after environment validation passes.
    after_packages() — Runs after Install Packages stage.
    before_iso()     — Runs before Create ISO stage.
    after_release()  — Runs after Release stage.
    cleanup()        — Always runs on success or failure.

Rules:
    - Never import from src.core or src.services directly.
    - Only read/write the BuildContext object passed as argument.
    - Never use global variables.
    - All exceptions are caught by PluginLoader and logged as warnings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.build_context import BuildContext


def initialize(context: "BuildContext") -> None:
    """Called once when the plugin is loaded before the pipeline starts."""
    context.plugin_data["example_plugin"] = {
        "initialized": True,
        "messages": [],
    }


def before_build(context: "BuildContext") -> None:
    """Called after environment validation, before package installation."""
    plugin = context.plugin_data.get("example_plugin", {})
    plugin.get("messages", []).append("before_build fired")


def after_packages(context: "BuildContext") -> None:
    """Called after the Install Packages stage completes."""
    plugin = context.plugin_data.get("example_plugin", {})
    plugin.get("messages", []).append("after_packages fired")


def before_iso(context: "BuildContext") -> None:
    """Called before the Create ISO stage begins."""
    plugin = context.plugin_data.get("example_plugin", {})
    plugin.get("messages", []).append("before_iso fired")


def after_release(context: "BuildContext") -> None:
    """Called after the Release stage completes successfully."""
    plugin = context.plugin_data.get("example_plugin", {})
    plugin.get("messages", []).append("after_release fired")


def cleanup(context: "BuildContext") -> None:
    """Always called at pipeline end — success or failure."""
    plugin = context.plugin_data.get("example_plugin", {})
    messages = plugin.get("messages", [])
    # In a real plugin, this would write a report or clean temp files.
    _ = messages  # Suppress unused variable warning in reference code.
