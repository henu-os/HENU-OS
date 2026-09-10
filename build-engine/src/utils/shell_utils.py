"""
HENU OS 3.0 — Build Engine
File: src/utils/shell_utils.py
Purpose: Stateless subprocess execution helpers.
         Wraps subprocess calls with consistent logging, timeout handling,
         and return-code checking used by package_installer and iso_builder.
"""

from __future__ import annotations

import subprocess
from typing import List, Optional, Tuple


class ShellCommandError(Exception):
    """Raised when a shell command exits with a non-zero return code."""
    def __init__(self, cmd: List[str], returncode: int, stderr: str) -> None:
        self.cmd = cmd
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(
            f"Command failed (exit {returncode}): {' '.join(cmd)}\n{stderr}"
        )


def run_command(
    cmd: List[str],
    cwd: Optional[str] = None,
    timeout: int = 3600,
    check: bool = True,
) -> Tuple[int, str, str]:
    """
    Execute a shell command synchronously.

    Args:
        cmd     — Command and arguments as a list of strings.
        cwd     — Working directory for the subprocess.
        timeout — Maximum seconds to allow (default 1 hour).
        check   — If True, raise ShellCommandError on non-zero exit.

    Returns:
        Tuple of (returncode, stdout, stderr).

    Raises:
        ShellCommandError — If check=True and returncode != 0.
        TimeoutError      — If the command exceeds timeout seconds.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError(
            f"Command timed out after {timeout}s: {' '.join(cmd)}"
        )

    if check and result.returncode != 0:
        raise ShellCommandError(cmd, result.returncode, result.stderr)

    return result.returncode, result.stdout, result.stderr


def run_command_stream(
    cmd: List[str],
    cwd: Optional[str] = None,
    timeout: int = 3600,
) -> int:
    """
    Execute a shell command and stream its stdout in real time.
    Useful for long-running processes like APT installs and ISO builds.

    Args:
        cmd     — Command and arguments.
        cwd     — Working directory.
        timeout — Maximum seconds to allow.

    Returns:
        Exit code of the process.

    Raises:
        TimeoutError — If the command exceeds timeout seconds.
    """
    import time

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd,
    )

    start = time.time()
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="", flush=True)
        if time.time() - start > timeout:
            proc.kill()
            raise TimeoutError(
                f"Command timed out after {timeout}s: {' '.join(cmd)}"
            )

    proc.wait()
    return proc.returncode
