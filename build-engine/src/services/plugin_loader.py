"""
HENU OS 3.0 — Build Engine
File: src/services/plugin_loader.py
Purpose: Plugin discovery, validation, and lifecycle management service.
         Implements IPluginLoader interface for Dependency Injection.

         Plugin Loading Lifecycle:
           1. Scan plugins/ directory for subdirectories.
           2. Read plugin.yaml manifest from each.
           3. Validate manifest schema and hook names.
           4. Check dependency version requirements.
           5. Load main.py module dynamically.
           6. Register hooks on EventBus.
           7. Execute hooks in priority order.

         Plugins receive only BuildContext — never global variables.

Dependencies:
    src.models.plugin_manifest  — PluginManifest data class.
    src.models.pipeline_stage   — IPluginLoader interface.
    src.utils.yaml_compat       — Manifest YAML parsing.
    src.core.event_bus          — Hook registration.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from src.models.pipeline_stage import IPluginLoader
from src.models.plugin_manifest import PluginManifest
from src.utils.yaml_compat import load_yaml_safe

if TYPE_CHECKING:
    from src.models.build_context import BuildContext
    from src.core.event_bus import EventBus


class PluginLoadError(Exception):
    """Raised when a plugin cannot be loaded due to manifest or code errors."""


class PluginLoader(IPluginLoader):
    """
    Plugin discovery, validation, and lifecycle manager.

    Usage:
        loader = PluginLoader(plugins_dir, event_bus, logger)
        loader.discover()
        loader.fire_hook("before_build", context)
        loader.fire_hook("after_release", context)
        loader.fire_hook("cleanup", context)
    """

    MANIFEST_FILENAME = "plugin.yaml"
    ENTRY_FILENAME    = "main.py"

    def __init__(
        self,
        plugins_dir: str,
        event_bus: "EventBus",
        logger: Any,
    ) -> None:
        self._plugins_dir = os.path.abspath(plugins_dir)
        self._event_bus   = event_bus
        self._logger      = logger
        self._manifests: List[PluginManifest] = []
        self._modules:   Dict[str, Any] = {}  # plugin_name -> loaded module

    # ---------------------------------------------------------------- #
    # IPluginLoader interface                                           #
    # ---------------------------------------------------------------- #

    def fire_hook(self, hook_name: str, context: "BuildContext") -> None:
        """
        Invoke a named lifecycle hook across all enabled plugins in priority order.

        Args:
            hook_name — One of the 6 plugin lifecycle hooks.
            context   — Current BuildContext passed to each plugin.
        """
        # Sort by priority (ascending — lower number runs first).
        for manifest in sorted(self._manifests, key=lambda m: m.priority):
            if not manifest.enabled:
                continue
            if hook_name not in manifest.hooks:
                continue

            module = self._modules.get(manifest.name)
            if module is None:
                continue

            hook_fn = getattr(module, hook_name, None)
            if callable(hook_fn):
                try:
                    self._logger.info(
                        f"Plugin '{manifest.name}' firing hook: {hook_name}"
                    )
                    hook_fn(context)
                except Exception as exc:
                    self._logger.warning(
                        f"Plugin '{manifest.name}' hook '{hook_name}' raised: {exc}"
                    )

    # ---------------------------------------------------------------- #
    # Discovery                                                         #
    # ---------------------------------------------------------------- #

    def discover(self) -> None:
        """
        Scan the plugins directory and load all valid, enabled plugins.
        Invalid or disabled plugins log warnings and are skipped.
        """
        if not os.path.isdir(self._plugins_dir):
            self._logger.info(
                f"No plugins directory found at: {self._plugins_dir}. Skipping."
            )
            return

        for entry in sorted(os.listdir(self._plugins_dir)):
            plugin_dir = os.path.join(self._plugins_dir, entry)
            if not os.path.isdir(plugin_dir):
                continue

            manifest_path = os.path.join(plugin_dir, self.MANIFEST_FILENAME)
            if not os.path.isfile(manifest_path):
                self._logger.warning(
                    f"Plugin directory '{entry}' missing {self.MANIFEST_FILENAME}. Skipped."
                )
                continue

            try:
                manifest = self._load_manifest(manifest_path, plugin_dir)
            except PluginLoadError as exc:
                self._logger.warning(str(exc))
                continue

            if not manifest.enabled:
                self._logger.info(f"Plugin '{manifest.name}' is disabled. Skipped.")
                continue

            try:
                module = self._load_module(manifest)
                self._modules[manifest.name]  = module
                self._manifests.append(manifest)
                self._logger.success(f"Plugin loaded: {manifest}")
            except PluginLoadError as exc:
                self._logger.warning(str(exc))

    # ---------------------------------------------------------------- #
    # Private helpers                                                   #
    # ---------------------------------------------------------------- #

    def _load_manifest(
        self, manifest_path: str, plugin_dir: str
    ) -> PluginManifest:
        """Parse, validate, and return a PluginManifest."""
        try:
            data = load_yaml_safe(manifest_path)
        except Exception as exc:
            raise PluginLoadError(
                f"Failed to parse {manifest_path}: {exc}"
            )

        required = ["name", "version", "author"]
        missing  = [k for k in required if k not in data]
        if missing:
            raise PluginLoadError(
                f"Plugin manifest {manifest_path} missing required keys: {missing}"
            )

        manifest = PluginManifest(
            name         = str(data["name"]),
            version      = str(data["version"]),
            author       = str(data["author"]),
            priority     = int(data.get("priority", 50)),
            enabled      = bool(data.get("enabled", True)),
            dependencies = list(data.get("dependencies", [])),
            hooks        = list(data.get("hooks", [])),
            plugin_dir   = plugin_dir,
        )

        invalid_hooks = manifest.validate_hooks()
        if invalid_hooks:
            raise PluginLoadError(
                f"Plugin '{manifest.name}' declares unknown hooks: {invalid_hooks}"
            )

        return manifest

    def _load_module(self, manifest: PluginManifest) -> Any:
        """Dynamically load the plugin's main.py module."""
        entry_path = os.path.join(manifest.plugin_dir, self.ENTRY_FILENAME)
        if not os.path.isfile(entry_path):
            raise PluginLoadError(
                f"Plugin '{manifest.name}' missing {self.ENTRY_FILENAME}."
            )

        spec = importlib.util.spec_from_file_location(
            f"henu_plugin_{manifest.name}", entry_path
        )
        if spec is None or spec.loader is None:
            raise PluginLoadError(
                f"Plugin '{manifest.name}' — cannot create module spec."
            )

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"henu_plugin_{manifest.name}"] = module

        try:
            spec.loader.exec_module(module)  # type: ignore[union-attr]
        except Exception as exc:
            raise PluginLoadError(
                f"Plugin '{manifest.name}' main.py raised on load: {exc}"
            )

        return module

    @property
    def loaded_plugins(self) -> List[PluginManifest]:
        """Returns list of successfully loaded plugin manifests."""
        return list(self._manifests)
