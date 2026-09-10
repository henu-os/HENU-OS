"""
HENU OS 3.0 — Build Engine
File: src/modules/release_manager.py
Purpose: Generates checksums, build manifests, and stages release artifacts.
"""

from __future__ import annotations
import os
import json
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger
from src.utils.file_utils import ensure_dir


class ReleaseManager:
    """Manages release output artifacts, manifests, and checksums."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = os.path.abspath(workspace_root)
        self._logger = logger

    def generate_manifest(self, context: BuildContext) -> str:
        release = context.config.get("release", {})
        manifest = {
            **context.summary(),
            "base_distribution": "Debian GNU/Linux 13 (Trixie)",
            "architecture": release.get("architecture", "amd64"),
            "os_version": release.get("version", "3.0.0-alpha.1"),
            "build_id": context.build_id,
            "git_commit": context.git_commit,
        }
        
        manifest_dir = os.path.join(self._workspace, "build-engine", "artifacts", "manifests")
        ensure_dir(manifest_dir)
        manifest_file = os.path.join(manifest_dir, f"{context.build_id}-manifest.json")
        
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            
        context.set_artifact("manifest", manifest_file)
        self._logger.info(f"Build manifest generated: {manifest_file}")
        return manifest_file
