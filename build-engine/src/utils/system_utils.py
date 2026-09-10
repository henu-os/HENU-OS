"""
HENU OS 3.0 — Build Engine
File: src/utils/system_utils.py
Purpose: Stateless host system inspection utilities.
         Used by the validator for resource and environment checks.
         No class state. Read-only system queries.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from typing import Dict, Optional, Tuple


def get_python_version() -> Tuple[int, int, int]:
    """
    Returns the current Python interpreter version as (major, minor, micro).
    """
    v = sys.version_info
    return (v.major, v.minor, v.micro)


def is_root() -> bool:
    """
    Returns True if the process is running with root/administrator privileges.
    On Linux/macOS: checks os.getuid() == 0.
    On Windows: always returns False (root is not applicable; document this).
    """
    if platform.system() == "Windows":
        # Windows does not have POSIX root. For build purposes, this
        # is always considered non-root. The Validate stage will issue
        # a WARNING instead of a CRITICAL error on Windows.
        return False
    return os.getuid() == 0  # type: ignore[attr-defined]


def get_free_disk_gb(path: str) -> float:
    """
    Returns free disk space in gigabytes for the filesystem containing path.

    Args:
        path — Any path on the target filesystem.

    Returns:
        Free space in GB as a float.
    """
    usage = shutil.disk_usage(path)
    return usage.free / (1024 ** 3)


def get_ram_gb() -> float:
    """
    Returns total system RAM in gigabytes.
    Uses /proc/meminfo on Linux. Falls back to platform-independent method.

    Returns:
        Total RAM in GB as a float, or -1.0 if detection fails.
    """
    try:
        if platform.system() == "Linux":
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        return kb / (1024 ** 2)
        elif platform.system() == "Windows":
            try:
                import ctypes
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                return stat.ullTotalPhys / (1024 ** 3)
            except Exception:
                pass
        # Fallback: attempt psutil (optional dependency)
        import psutil  # type: ignore
        return psutil.virtual_memory().total / (1024 ** 3)
    except Exception:
        return -1.0


def get_cpu_count() -> int:
    """
    Returns the number of logical CPU cores available.
    """
    return os.cpu_count() or 1


def tool_exists(tool_name: str) -> bool:
    """
    Returns True if a CLI tool is found in the system PATH.

    Args:
        tool_name — Binary name (e.g., 'debootstrap', 'lb', 'xorriso').
    """
    return shutil.which(tool_name) is not None


def get_git_commit(repo_path: str) -> str:
    """
    Returns the current HEAD commit hash for the git repository at repo_path.
    Returns an empty string if the path is not a git repo or git is unavailable.

    Args:
        repo_path — Path to the repository root.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def check_internet(host: str = "8.8.8.8", timeout: int = 3) -> bool:
    """
    Returns True if the host is reachable via ping.
    Used for the internet connectivity pre-flight check.

    Args:
        host    — IP or hostname to ping.
        timeout — Timeout in seconds.
    """
    try:
        param = "-n" if platform.system() == "Windows" else "-c"
        result = subprocess.run(
            ["ping", param, "1", "-W", str(timeout), host],
            capture_output=True, timeout=timeout + 2
        )
        return result.returncode == 0
    except Exception:
        return False


def get_platform_info() -> Dict[str, str]:
    """
    Returns a dictionary of host platform metadata for manifest generation.
    """
    return {
        "os":           platform.system(),
        "os_release":   platform.release(),
        "architecture": platform.machine(),
        "python":       platform.python_version(),
        "hostname":     platform.node(),
    }
