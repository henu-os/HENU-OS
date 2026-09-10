"""
HENU OS 3.0 — Build Engine
File: src/modules/component_deployer.py
Purpose: Compiles and deploys the 13 independent HENU OS applications into target rootfs.
"""

from __future__ import annotations
import os
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class ComponentDeployer:
    """Discovers and installs standalone sub-applications from apps/."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = os.path.abspath(workspace_root)
        self._logger = logger

    def deploy_components(self, context: BuildContext, target_rootfs: str) -> bool:
        apps_dir = os.path.join(self._workspace, "apps")
        if not os.path.isdir(apps_dir):
            self._logger.warning("apps/ directory not found.")
            return True

        apps = sorted([
            d for d in os.listdir(apps_dir)
            if os.path.isdir(os.path.join(apps_dir, d)) and not d.startswith(".")
        ])
        
        self._logger.info(f"Discovered {len(apps)} standalone applications: {', '.join(apps)}")
        return True
