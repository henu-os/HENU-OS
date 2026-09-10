"""
HENU OS 3.0 — Build Engine
File: src/models/plugin_manifest.py
Purpose: Parsed, validated data model for plugin.yaml manifests.
         PluginLoader reads plugin.yaml and produces a PluginManifest.
         No plugin code is loaded until its manifest has been validated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PluginManifest:
    """
    Represents the contents of a validated plugin.yaml file.

    Attributes:
        name         — Unique plugin identifier (slug, no spaces).
        version      — Plugin version string (SemVer recommended).
        author       — Author or team name.
        priority     — Load order weight; lower numbers load first (default 50).
        enabled      — Whether the plugin is active.
        dependencies — List of dependency strings ('core >= 3.0.0').
        hooks        — List of lifecycle hook names this plugin implements.
        plugin_dir   — Absolute path to the plugin directory.
    """
    name: str
    version: str
    author: str
    priority: int = 50
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    plugin_dir: str = ""

    # Supported lifecycle hook names.
    VALID_HOOKS: List[str] = field(default_factory=lambda: [
        "initialize",
        "before_build",
        "after_packages",
        "before_iso",
        "after_release",
        "cleanup",
    ])

    def validate_hooks(self) -> List[str]:
        """
        Returns a list of unrecognised hook names declared in this manifest.
        An empty list means all declared hooks are valid.
        """
        return [h for h in self.hooks if h not in self.VALID_HOOKS]

    def __str__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"Plugin({self.name} v{self.version} by {self.author} [{status}] priority={self.priority})"
