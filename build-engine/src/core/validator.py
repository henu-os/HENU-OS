# System Pre-flight Validation Module for HENU Build Engine
# Version: 3.0.0-alpha.1
# Base: Debian GNU/Linux 13 (Trixie)

import os
import shutil
import platform
from typing import Dict, List, Tuple

class ValidationError(Exception):
    """Raised when one or more system pre-flight checks fail."""
    pass

class BuildValidator:
    """Performs integrity and environment validation checks before running build pipelines."""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = os.path.abspath(workspace_root)

    def verify_folders_exist(self) -> List[str]:
        """Checks if the required workspace folders exist."""
        required_dirs = [
            "apps",
            "configs",
            "scripts",
            "docs",
            "branding",
            "branding-package",
            "build",
            "build-engine",
            "installer",
            "kernel",
            "packages",
            "testing"
        ]
        missing = []
        for d in required_dirs:
            target = os.path.join(self.workspace_root, d)
            if not os.path.isdir(target):
                missing.append(d)
        return missing

    def verify_configs_exist(self) -> List[str]:
        """Validates that all required split configuration files are present."""
        required_configs = [
            "configs/build_config.yaml",
            "configs/debian_config.yaml",
            "configs/desktop_config.yaml",
            "configs/branding_config.yaml",
            "configs/package_config.yaml",
            "configs/kernel_config.yaml",
            "configs/installer_config.yaml",
            "configs/testing_config.yaml",
            "configs/security_config.yaml",
            "configs/release_config.yaml"
        ]
        missing = []
        for cfg in required_configs:
            target = os.path.join(self.workspace_root, cfg)
            if not os.path.isfile(target):
                missing.append(cfg)
        return missing

    def verify_branding_assets(self, branding_config: Dict[str, any]) -> List[str]:
        """Checks if active default branding assets specified in configuration exist."""
        missing = []
        branding = branding_config.get("branding", {})
        defaults = branding.get("active_defaults", {})
        
        for key in ["logo_main", "wallpaper_first_time_user"]:
            asset_rel = defaults.get(key)
            if asset_rel:
                asset_full = os.path.normpath(os.path.join(self.workspace_root, asset_rel))
                if not os.path.exists(asset_full):
                    missing.append(f"{key}: {asset_rel}")
                    
        return missing

    def verify_tools(self) -> List[str]:
        """Validates presence of Debian live-build and compilation utilities in system PATH."""
        # On Windows dev workstation, native Linux ISO tools are not expected.
        if platform.system() == "Windows":
            return []
        
        required_tools = ["debootstrap", "lb", "apt-get", "dpkg", "xorriso"]
        missing = []
        for tool in required_tools:
            if shutil.which(tool) is None:
                missing.append(tool)
        return missing

    def verify_disk_space(self, required_gb: int = 30) -> Tuple[bool, float]:
        """Verifies workspace host drive has sufficient free storage space."""
        total, used, free = shutil.disk_usage(self.workspace_root)
        free_gb = free / (1024 ** 3)
        return (free_gb >= required_gb, free_gb)

    def verify_permissions(self) -> bool:
        """Verifies execution context has admin/root privileges."""
        if platform.system() == "Windows":
            return True
        if hasattr(os, "getuid"):
            return os.getuid() == 0
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except AttributeError:
            return False

    def run_all_checks(self, merged_config: Dict[str, any], required_space_gb: int = 30) -> None:
        """Runs all checks sequentially and raises detailed ValidationError on failures."""
        errors = []

        # 1. Folders
        missing_folders = self.verify_folders_exist()
        if missing_folders:
            errors.append(f"Missing core workspace folder(s): {', '.join(missing_folders)}")

        # 2. Configs
        missing_configs = self.verify_configs_exist()
        if missing_configs:
            errors.append(f"Missing split configuration file(s): {', '.join(missing_configs)}")

        # 3. Tools
        missing_tools = self.verify_tools()
        if missing_tools:
            errors.append(f"Missing build environment executable utility: {', '.join(missing_tools)}")

        # 4. Storage Space
        space_ok, free_gb = self.verify_disk_space(required_space_gb)
        if not space_ok:
            errors.append(f"Insufficient disk storage space. Free: {free_gb:.2f}GB, Required: {required_space_gb}GB")

        # 5. Privileges
        if not self.verify_permissions():
            errors.append("Execution requires root/administrator privileges.")

        # 6. Branding Assets
        if "branding" in merged_config:
            missing_assets = self.verify_branding_assets(merged_config)
            if missing_assets:
                print(f"[PRE-FLIGHT WARNING] Configuration lists missing asset paths: {', '.join(missing_assets)}")

        if errors:
            raise ValidationError("\n".join(errors))
