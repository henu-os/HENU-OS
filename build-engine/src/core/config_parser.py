# Configuration Parser Module for HENU Build Engine
# Version: 3.0.0-alpha.1

import os
from typing import Any, Dict, List

class ConfigValidationError(Exception):
    """Raised when configuration validation constraints are breached."""
    pass

def _parse_yaml_fallback(file_content: str) -> Dict[str, Any]:
    """Fallback basic YAML parser for bootstrapping environments lacking PyYAML."""
    result: Dict[str, Any] = {}
    current_key: str = ""
    current_list: List[str] = []
    in_list: bool = False
    in_section: str = ""

    lines = file_content.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Handle list items
        if stripped.startswith("-"):
            val = stripped.lstrip("-").strip().strip('"').strip("'")
            if in_list:
                current_list.append(val)
            continue
        else:
            if in_list and current_key:
                if in_section:
                    if in_section not in result:
                        result[in_section] = {}
                    result[in_section][current_key] = current_list
                else:
                    result[current_key] = current_list
                in_list = False
                current_list = []
                current_key = ""

        # Check section headings (no indentation or minor)
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            parts = line.split(":", 1)
            in_section = parts[0].strip()
            result[in_section] = {}
            continue

        # Handle key-values
        if ":" in line:
            parts = line.split(":", 1)
            k = parts[0].strip()
            v = parts[1].strip().strip('"').strip("'")
            
            # Check if it starts a list
            if not v:
                current_key = k
                in_list = True
                current_list = []
            else:
                # Boolean conversion
                if v.lower() == "true":
                    v_parsed: Any = True
                elif v.lower() == "false":
                    v_parsed = False
                elif v.isdigit():
                    v_parsed = int(v)
                else:
                    v_parsed = v
                
                if in_section:
                    if in_section not in result:
                        result[in_section] = {}
                    result[in_section][k] = v_parsed
                else:
                    result[k] = v_parsed

    # Append any remaining open lists
    if in_list and current_key:
        if in_section:
            if in_section not in result:
                result[in_section] = {}
            result[in_section][current_key] = current_list
        else:
            result[current_key] = current_list

    return result

def load_build_config(config_path: str) -> Dict[str, Any]:
    """Loads and validates the build YAML configuration."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Always use the robust custom fallback parser to avoid PyYAML C-extension crashes on Python 3.14
    config_data = _parse_yaml_fallback(content)

    return config_data
