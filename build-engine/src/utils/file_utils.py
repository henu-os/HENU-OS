"""
HENU OS 3.0 — Build Engine
File: src/utils/file_utils.py
Purpose: Stateless filesystem helper functions.
         Used by workspace preparation, branding applier, and release manager.
         No class state. No side effects beyond the filesystem.
"""

from __future__ import annotations

import os
import shutil
from typing import List


def ensure_dir(path: str) -> str:
    """
    Create a directory and all intermediate parents if they do not exist.

    Args:
        path — Target directory path.

    Returns:
        The absolute path to the directory.
    """
    abs_path = os.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def purge_dir(path: str) -> None:
    """
    Delete all contents of a directory without removing the directory itself.
    Safe to call on a non-existent path.
    Enforces strict safety checks to prevent accidental root or system deletion.

    Args:
        path — Target directory to purge.
    """
    if not path or not path.strip():
        raise ValueError("purge_dir received empty path — aborted for safety.")

    abs_path = os.path.abspath(path)

    # Safety: Do not purge filesystem root or unsafe short paths
    unsafe_roots = ["/", "\\", "c:\\", "c:/", "d:\\", "d:/", "h:\\", "h:/"]
    if abs_path.lower().rstrip("/\\") in [r.lower().rstrip("/\\") for r in unsafe_roots]:
        raise PermissionError(f"CRITICAL SAFETY VIOLATION: Refusing to purge root directory: {abs_path}")

    if not os.path.isdir(abs_path):
        return

    for item in os.listdir(abs_path):
        item_path = os.path.join(abs_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def copy_file(src: str, dst: str) -> None:
    """
    Copy a single file from src to dst, creating parent directories as needed.

    Args:
        src — Source file path.
        dst — Destination file path (not directory).

    Raises:
        FileNotFoundError — If src does not exist.
    """
    if not os.path.isfile(src):
        raise FileNotFoundError(f"Source file not found: {src}")
    ensure_dir(os.path.dirname(dst))
    shutil.copy2(src, dst)


def copy_tree(src: str, dst: str) -> None:
    """
    Recursively copy a directory tree from src to dst.
    Overwrites existing files in dst.

    Args:
        src — Source directory.
        dst — Destination directory.

    Raises:
        FileNotFoundError — If src does not exist or is not a directory.
    """
    if not os.path.isdir(src):
        raise FileNotFoundError(f"Source directory not found: {src}")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def list_files(directory: str, extension: str = "") -> List[str]:
    """
    List all files in a directory, optionally filtered by extension.

    Args:
        directory — Path to scan.
        extension — File extension filter (e.g., '.yaml'). Empty = all files.

    Returns:
        List of absolute file paths.
    """
    result: List[str] = []
    if not os.path.isdir(directory):
        return result
    for root, _, files in os.walk(directory):
        for fname in files:
            if not extension or fname.endswith(extension):
                result.append(os.path.join(root, fname))
    return result


def file_size_mb(path: str) -> float:
    """
    Return the size of a file in megabytes.

    Args:
        path — Absolute or relative file path.

    Returns:
        File size as a float (MB). Returns 0.0 if file does not exist.
    """
    if not os.path.isfile(path):
        return 0.0
    return os.path.getsize(path) / (1024 * 1024)
