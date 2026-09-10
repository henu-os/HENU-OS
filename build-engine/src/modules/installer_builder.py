"""
HENU OS 3.0 — Build Engine
File: src/modules/installer_builder.py
Purpose: Modular installer integration builder (Calamares and Debian-Installer preseed).
"""

from __future__ import annotations
import os
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class InstallerBuilder:
    """Configures installer payload inside live filesystem."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = os.path.abspath(workspace_root)
        self._logger = logger

    def configure_installer(self, context: BuildContext, target_rootfs: str) -> bool:
        installer_cfg = context.config.get("installer", {})
        engine = installer_cfg.get("default_engine", "calamares")
        self._logger.info(f"Configuring installer subsystem using engine: {engine}")
        return True
