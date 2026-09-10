"""
HENU OS 3.0 — Build Engine
File: src/models/build_context.py
Purpose: Immutable shared state object passed between every pipeline stage.
         Replaces all global variables. Every stage reads, modifies, and passes
         this forward. Contains the full snapshot of a single build run.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BuildContext:
    """
    The central immutable data carrier for a single HENU OS build run.

    Passed into every pipeline stage. No stage may read from global scope.
    Stages append to `stage_log` and set their outputs in `artifacts`.

    Attributes:
        workspace_root  — Absolute path to the HENU-OS project root.
        build_id        — Unique identifier for this build run (timestamp-based).
        build_profile   — Active profile: 'development', 'testing', 'release', 'enterprise'.
        config          — Fully merged configuration dictionary.
        git_commit      — Current HEAD commit hash (empty if not in git repo).
        config_hash     — MD5 fingerprint of the merged configuration.
        start_time      — Unix epoch when the build started.
        stage_log       — Ordered list of completed stage names.
        artifacts       — Dict mapping artifact keys to output paths.
        metadata        — Arbitrary metadata bag for stage communication.
        errors          — Non-fatal error accumulator.
        plugin_data     — Namespace for plugins to store cross-hook data.
    """

    workspace_root: str
    build_id: str = field(default_factory=lambda: f"henu-{int(time.time())}")
    build_profile: str = "development"
    config: Dict[str, Any] = field(default_factory=dict)
    git_commit: str = ""
    config_hash: str = ""
    start_time: float = field(default_factory=time.time)
    stage_log: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    plugin_data: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------ #
    # Convenience helpers                                                  #
    # ------------------------------------------------------------------ #

    def elapsed(self) -> float:
        """Returns total elapsed build time in seconds."""
        return time.time() - self.start_time

    def mark_stage_done(self, stage_name: str) -> None:
        """Record that a pipeline stage has completed successfully."""
        self.stage_log.append(stage_name)

    def set_artifact(self, key: str, path: str) -> None:
        """Register an output artifact path under a named key."""
        self.artifacts[key] = os.path.abspath(path)

    def get_artifact(self, key: str) -> Optional[str]:
        """Retrieve a registered artifact path by key, or None."""
        return self.artifacts.get(key)

    def add_error(self, message: str) -> None:
        """Accumulate a non-fatal error without stopping the pipeline."""
        self.errors.append(message)

    def has_errors(self) -> bool:
        """Returns True if non-fatal errors have been accumulated."""
        return len(self.errors) > 0

    def summary(self) -> Dict[str, Any]:
        """Returns a JSON-serialisable summary for manifest generation."""
        return {
            "build_id": self.build_id,
            "build_profile": self.build_profile,
            "git_commit": self.git_commit,
            "config_hash": self.config_hash,
            "start_time": self.start_time,
            "elapsed_seconds": round(self.elapsed(), 2),
            "stages_completed": self.stage_log,
            "artifacts": self.artifacts,
            "errors": self.errors,
        }
