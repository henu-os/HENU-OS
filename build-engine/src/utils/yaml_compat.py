"""
HENU OS 3.0 — Build Engine
File: src/utils/yaml_compat.py
Purpose: Isolated compatibility shim for YAML parsing supporting arbitrary nesting.
"""

from __future__ import annotations

import re
import sys
from typing import Any, Dict, List, Tuple


def load_yaml_safe(path: str) -> Dict[str, Any]:
    """
    Load a YAML file using PyYAML if available and stable.
    Falls back to the internal shim parser on Python 3.14+ or if PyYAML is absent.
    """
    if sys.version_info >= (3, 14):
        return _shim_parse(path)

    try:
        import yaml  # type: ignore
        with open(path, "r", encoding="utf-8") as f:
            result = yaml.safe_load(f)
            return result if isinstance(result, dict) else {}
    except (ImportError, Exception):
        return _shim_parse(path)


def _shim_parse(path: str) -> Dict[str, Any]:
    """
    Indentation-based YAML parser supporting arbitrarily nested dictionaries and lists.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    lines = raw_text.splitlines()

    def coerce(value: str) -> Any:
        v = value.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            return v[1:-1]
        if v.lower() == "true":
            return True
        if v.lower() == "false":
            return False
        if v.isdigit():
            return int(v)
        try:
            return float(v)
        except ValueError:
            return v

    def parse_block(line_idx: int, current_indent: int) -> Tuple[Any, int]:
        # Peek first content line to decide if this block is a list or dict
        is_list = False
        scan_idx = line_idx
        while scan_idx < len(lines):
            line = lines[scan_idx]
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                scan_idx += 1
                continue
            indent = len(line) - len(line.lstrip(" "))
            if indent < current_indent:
                break
            if stripped.startswith("- "):
                is_list = True
            break

        if is_list:
            result_list: List[Any] = []
            idx = line_idx
            while idx < len(lines):
                line = lines[idx]
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    idx += 1
                    continue
                indent = len(line) - len(line.lstrip(" "))
                if indent < current_indent:
                    break
                if stripped.startswith("- "):
                    item_str = stripped[2:].strip()
                    if ":" in item_str and not item_str.startswith("http://") and not item_str.startswith("https://"):
                        # List item is a dict entry
                        k, v = item_str.split(":", 1)
                        k = k.strip()
                        v = v.strip()
                        if not v:
                            sub_val, idx = parse_block(idx + 1, indent + 2)
                            result_list.append({k: sub_val})
                            continue
                        else:
                            result_list.append({k: coerce(v)})
                            idx += 1
                            continue
                    else:
                        result_list.append(coerce(item_str))
                        idx += 1
                else:
                    break
            return result_list, idx
        else:
            result_dict: Dict[str, Any] = {}
            idx = line_idx
            while idx < len(lines):
                line = lines[idx]
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    idx += 1
                    continue
                indent = len(line) - len(line.lstrip(" "))
                if indent < current_indent:
                    break
                if ":" in stripped:
                    # Remove trailing comments
                    clean_line = stripped
                    if " #" in clean_line and not (clean_line.startswith('"') or clean_line.startswith("'")):
                        clean_line = clean_line.split(" #")[0].strip()
                    
                    parts = clean_line.split(":", 1)
                    k = parts[0].strip()
                    v = parts[1].strip() if len(parts) > 1 else ""
                    if not v:
                        # Value is in the next indented block
                        sub_val, idx = parse_block(idx + 1, indent + 1)
                        result_dict[k] = sub_val
                    else:
                        result_dict[k] = coerce(v)
                        idx += 1
                else:
                    idx += 1
            return result_dict, idx

    parsed, _ = parse_block(0, 0)
    return parsed if isinstance(parsed, dict) else {}
