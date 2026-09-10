"""
HENU OS 3.0 — Build Engine
File: src/modules/kernel_manager.py
Purpose: Orchestrates Debian kernel package deployment and boot parameters.
"""

from __future__ import annotations
import os
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class KernelManager:
    """Manages kernel image and initramfs configuration."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = os.path.abspath(workspace_root)
        self._logger = logger

    def configure_kernel(self, context: BuildContext, target_rootfs: str) -> bool:
        kernel_cfg = context.config.get("kernel", {})
        strategy = kernel_cfg.get("strategy", "debian_package")
        
        if strategy == "debian_package":
            pkg = kernel_cfg.get("debian", {}).get("image_package", "linux-image-amd64")
            self._logger.info(f"Using Debian official kernel strategy: {pkg}")
        else:
            self._logger.info("Custom compiled kernel strategy selected.")
            
        boot_params = kernel_cfg.get("boot_parameters", [])
        self._logger.info(f"Registered kernel boot parameters: {' '.join(boot_params)}")
        return True
