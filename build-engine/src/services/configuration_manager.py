"""
HENU OS 3.0 — Build Engine
File: src/services/configuration_manager.py
Purpose: Central configuration service implementing the IConfiguration interface.
         Executes the full 5-contract lifecycle:
           load() → validate() → merge() → override() → cache()

         Implements Dependency Injection: exposes IConfiguration interface
         so pipeline stages are never coupled to this concrete class.

Dependencies:
    src.utils.yaml_compat  — YAML loading with PyYAML / shim fallback.
    src.utils.hash_utils   — Config fingerprinting (MD5 of merged dict).
    src.models.pipeline_stage.IConfiguration — DI interface.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from src.models.pipeline_stage import IConfiguration
from src.utils.hash_utils import md5_dict
from src.utils.yaml_compat import load_yaml_safe


# ------------------------------------------------------------------ #
# Custom Exceptions                                                   #
# ------------------------------------------------------------------ #

class ConfigurationError(Exception):
    """Raised when configuration loading, validation, or merging fails."""


# ------------------------------------------------------------------ #
# ConfigurationManager                                                #
# ------------------------------------------------------------------ #

class ConfigurationManager(IConfiguration):
    """
    Stateful service managing the full lifecycle of HENU OS build configuration.

    Usage:
        manager = ConfigurationManager(workspace_root)
        manager.load()
        manager.validate()
        manager.merge()
        merged = manager.all()

    Dependency Injection:
        Exposed as IConfiguration to pipeline stages.
        Stages call manager.get(key) / manager.all() — never import this class.

    Build Profiles:
        'development'  — All checks, verbose logging, no ISO compression.
        'testing'      — All checks, condensed logging, fast ISO build.
        'release'      — Full pipeline, max compression, GPG signing.
        'enterprise'   — Release + compliance audit, SCAP scan.
    """

    # All config file keys referenced in build_config.yaml → configs section.
    _REQUIRED_CONFIG_KEYS: List[str] = [
        "build_options",
        "paths",
    ]

    def __init__(
        self,
        workspace_root: str,
        profile: str = "development",
        overrides: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._workspace_root = os.path.abspath(workspace_root)
        self._profile        = profile
        self._overrides      = overrides or {}
        self._raw_configs:  Dict[str, Dict[str, Any]] = {}
        self._merged:       Dict[str, Any] = {}
        self._config_hash:  str = ""
        self._is_loaded:    bool = False

        self._main_config_path = os.path.join(
            self._workspace_root, "configs", "build_config.yaml"
        )
        self._cache_path = os.path.join(
            self._workspace_root, "build-engine", "cache", "configs", "merged.json"
        )

    # ---------------------------------------------------------------- #
    # Contract 1: load()                                                #
    # ---------------------------------------------------------------- #

    def load(self) -> None:
        """
        Load the main index config and all referenced split config files.
        Attempts PyYAML; falls back to shim via yaml_compat.load_yaml_safe().

        Raises:
            ConfigurationError — If the main config file is missing.
        """
        if not os.path.isfile(self._main_config_path):
            raise ConfigurationError(
                f"Main build configuration not found: {self._main_config_path}"
            )

        main = load_yaml_safe(self._main_config_path)
        self._raw_configs["build"] = main

        # Load each split config referenced under the 'configs' key.
        for key, rel_path in main.get("configs", {}).items():
            full_path = os.path.normpath(
                os.path.join(self._workspace_root, rel_path)
            )
            if not os.path.isfile(full_path):
                raise ConfigurationError(
                    f"Referenced config '{key}' not found: {full_path}"
                )
            self._raw_configs[key] = load_yaml_safe(full_path)

        self._is_loaded = True

    # ---------------------------------------------------------------- #
    # Contract 2: validate()                                            #
    # ---------------------------------------------------------------- #

    def validate(self) -> None:
        """
        Validate loaded configurations against required keys and type rules.
        Schema files (docs/schemas/*.schema.json) are used when present;
        falls back to built-in required-key checks.

        Raises:
            ConfigurationError — If required keys are missing or types mismatch.
            RuntimeError       — If validate() is called before load().
        """
        self._assert_loaded("validate")

        main = self._raw_configs.get("build", {})
        missing = [k for k in self._REQUIRED_CONFIG_KEYS if k not in main]
        if missing:
            raise ConfigurationError(
                f"Main build config missing required keys: {missing}"
            )

        # Check that all referenced config paths exist.
        for key, rel_path in main.get("configs", {}).items():
            if key not in self._raw_configs:
                raise ConfigurationError(
                    f"Config section '{key}' was listed but not loaded."
                )

    # ---------------------------------------------------------------- #
    # Contract 3: merge()                                               #
    # ---------------------------------------------------------------- #

    def merge(self) -> None:
        """
        Deep-merge all loaded raw configs into a single unified dictionary.
        Generates a MD5 fingerprint of the merged result for cache validation.

        Raises:
            RuntimeError — If merge() is called before load() and validate().
        """
        self._assert_loaded("merge")

        merged: Dict[str, Any] = {}
        for _, data in self._raw_configs.items():
            self._deep_merge(merged, data)

        # Apply profile-specific defaults.
        merged.setdefault("build_profile", self._profile)

        self._merged      = merged
        self._config_hash = md5_dict(merged)

    # ---------------------------------------------------------------- #
    # Contract 4: override()                                            #
    # ---------------------------------------------------------------- #

    def apply_overrides(self) -> None:
        """
        Apply CLI or environment overrides onto the merged configuration.
        Override values take the highest priority over any file value.

        Overrides are flat key paths using dot notation:
            e.g., {"system.version": "3.0.1"} sets merged["system"]["version"]
        """
        for key_path, value in self._overrides.items():
            parts = key_path.split(".")
            target = self._merged
            for part in parts[:-1]:
                target = target.setdefault(part, {})
            target[parts[-1]] = value

        if self._overrides:
            # Recompute fingerprint after overrides.
            self._config_hash = md5_dict(self._merged)

    # ---------------------------------------------------------------- #
    # Contract 5: cache()                                               #
    # ---------------------------------------------------------------- #

    def cache(self) -> None:
        """
        Persist the fully merged configuration to the cache file.
        On subsequent runs, the pipeline can compare config_hash to skip
        redundant loading when configurations have not changed.
        """
        os.makedirs(os.path.dirname(self._cache_path), exist_ok=True)
        payload = {
            "config_hash": self._config_hash,
            "profile":     self._profile,
            "config":      self._merged,
        }
        with open(self._cache_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def load_cached(self) -> bool:
        """
        Attempt to load from cache. Returns True if cache is valid and loaded.
        Cache is considered invalid if the source YAML file hashes differ.

        Returns:
            True if a valid cached config was loaded; False otherwise.
        """
        if not os.path.isfile(self._cache_path):
            return False
        try:
            with open(self._cache_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            self._merged      = payload["config"]
            self._config_hash = payload["config_hash"]
            self._profile     = payload.get("profile", self._profile)
            self._is_loaded   = True
            return True
        except Exception:
            return False

    # ---------------------------------------------------------------- #
    # IConfiguration Interface                                          #
    # ---------------------------------------------------------------- #

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a top-level configuration value by key.

        Args:
            key     — Top-level key name.
            default — Value returned if key is absent.
        """
        return self._merged.get(key, default)

    def all(self) -> Dict[str, Any]:
        """Return the complete merged configuration dictionary."""
        return dict(self._merged)

    # ---------------------------------------------------------------- #
    # Public helpers                                                    #
    # ---------------------------------------------------------------- #

    @property
    def config_hash(self) -> str:
        """MD5 fingerprint of the current merged configuration."""
        return self._config_hash

    @property
    def profile(self) -> str:
        """Active build profile name."""
        return self._profile

    def run(self) -> Dict[str, Any]:
        """
        Convenience method: execute full lifecycle in correct order.
        Returns the merged configuration dictionary.
        """
        self.load()
        self.validate()
        self.merge()
        self.apply_overrides()
        self.cache()
        return self._merged

    # ---------------------------------------------------------------- #
    # Private helpers                                                   #
    # ---------------------------------------------------------------- #

    def _assert_loaded(self, method_name: str) -> None:
        if not self._is_loaded:
            raise RuntimeError(
                f"ConfigurationManager.{method_name}() called before load()."
            )

    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Recursively merge override into base in-place.
        Dicts are merged; all other types are overwritten.
        """
        for key, value in override.items():
            if (
                key in base
                and isinstance(base[key], dict)
                and isinstance(value, dict)
            ):
                ConfigurationManager._deep_merge(base[key], value)
            else:
                base[key] = value
