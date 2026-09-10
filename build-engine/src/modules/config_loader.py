# Configuration Merger Module for HENU Build Engine
# Version: 3.0.0-alpha.1

import os
from typing import Dict, Any
from src.core.config_parser import load_build_config

class ConfigLoader:
    """Loads split YAML configuration files and merges them into a single settings dictionary."""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = os.path.abspath(workspace_root)
        self.main_config_path = os.path.join(self.workspace_root, "configs", "build_config.yaml")

    def load_and_merge(self) -> Dict[str, Any]:
        """Loads all split YAML files defined in the index configurations and merges them."""
        # 1. Load main build config index
        main_config = load_build_config(self.main_config_path)
        merged: Dict[str, Any] = {}
        merged.update(main_config)

        # 2. Iterate and merge defined split configurations
        configs_to_merge = main_config.get("configs", {})
        for config_key, relative_path in configs_to_merge.items():
            full_path = os.path.normpath(os.path.join(self.workspace_root, relative_path))
            
            # Load config (loads via fallback if pyyaml is missing)
            config_part = load_build_config(full_path)
            
            # Merge dictionary elements
            merged.update(config_part)

        return merged
