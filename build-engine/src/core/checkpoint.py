"""
HENU OS 3.0 — Build Engine
File: src/core/checkpoint.py
Purpose: Stage completion checkpoint manager.
         After each successful pipeline stage, CheckpointManager writes
         the stage name to a JSON file. On restart after partial failure,
         the pipeline reads the checkpoint and skips already-completed stages.

         This prevents re-downloading packages or rebuilding the chroot
         environment after an ISO assembly failure.

Usage:
    cp = CheckpointManager(workspace_root)
    cp.record("Install Packages")
    completed = cp.completed_stages()
    cp.clear()
"""

from __future__ import annotations

import json
import os
import time
from typing import List


class CheckpointManager:
    """
    Persists completed pipeline stage names across build runs.

    Checkpoint file location:
        build-engine/artifacts/checkpoint.json

    File format:
        {
          "build_id": "henu-1721234567",
          "timestamp": 1721234567.123,
          "completed_stages": ["Read Config", "Validate", "Prepare Workspace"]
        }
    """

    CHECKPOINT_FILENAME = "checkpoint.json"

    def __init__(self, artifacts_dir: str) -> None:
        self._artifacts_dir    = os.path.abspath(artifacts_dir)
        self._checkpoint_path  = os.path.join(
            self._artifacts_dir, self.CHECKPOINT_FILENAME
        )
        self._completed: List[str] = []
        self._build_id: str = ""
        os.makedirs(self._artifacts_dir, exist_ok=True)

    def load(self, build_id: str) -> bool:
        """
        Load existing checkpoint for a build_id.
        Returns True if checkpoint exists and matches build_id.
        Call this at pipeline start to determine resume state.

        Args:
            build_id — The current build run identifier.

        Returns:
            True if a matching checkpoint was found and loaded.
        """
        if not os.path.isfile(self._checkpoint_path):
            self._build_id = build_id
            return False

        try:
            with open(self._checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("build_id") != build_id:
                # Checkpoint is from a different build — start fresh.
                self._build_id   = build_id
                self._completed  = []
                return False

            self._build_id  = build_id
            self._completed = data.get("completed_stages", [])
            return len(self._completed) > 0

        except (json.JSONDecodeError, KeyError):
            self._build_id  = build_id
            self._completed = []
            return False

    def record(self, stage_name: str) -> None:
        """
        Record that a stage has completed and persist to disk.

        Args:
            stage_name — The name of the completed stage.
        """
        if stage_name not in self._completed:
            self._completed.append(stage_name)
        self._write()

    def is_done(self, stage_name: str) -> bool:
        """
        Returns True if a stage is already recorded as completed.

        Args:
            stage_name — The stage name to check.
        """
        return stage_name in self._completed

    def completed_stages(self) -> List[str]:
        """Returns the list of completed stage names."""
        return list(self._completed)

    def clear(self) -> None:
        """
        Remove the checkpoint file and reset state.
        Call this at the start of a fresh (non-resume) build.
        """
        self._completed = []
        if os.path.isfile(self._checkpoint_path):
            os.remove(self._checkpoint_path)

    def _write(self) -> None:
        """Persist the current checkpoint state to disk."""
        payload = {
            "build_id":        self._build_id,
            "timestamp":       time.time(),
            "completed_stages": self._completed,
        }
        with open(self._checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
