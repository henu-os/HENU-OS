"""
HENU OS 3.0 — Build Engine
File: src/core/progress.py
Purpose: Terminal progress reporter for the build pipeline.
         Prints stage progress bars and elapsed time summaries
         to stdout without interfering with file logging.

Usage:
    pr = ProgressReporter(total_stages=14)
    pr.start_stage("Install Packages", 5)
    pr.complete_stage("Install Packages", elapsed=12.4)
    pr.print_summary(context)
"""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.build_context import BuildContext

# ANSI codes used only for terminal output.
_GREEN  = "\033[92m"
_YELLOW = "\033[93m"
_CYAN   = "\033[96m"
_BOLD   = "\033[1m"
_RESET  = "\033[0m"
_FILL   = "█"
_EMPTY  = "░"


def _supports_color() -> bool:
    """Returns True if the terminal likely supports ANSI color codes."""
    return os.environ.get("NO_COLOR") is None and os.isatty(1)


class ProgressReporter:
    """
    Lightweight terminal progress reporter for the HENU Build Engine.

    Prints a progress bar and stage status to stdout.
    Does NOT write to log files — that is handled by LoggingManager.
    """

    BAR_WIDTH = 30

    def __init__(self, total_stages: int) -> None:
        self._total       = total_stages
        self._current     = 0
        self._start_time  = time.time()
        self._use_color   = _supports_color()

    def start_stage(self, stage_name: str, stage_index: int) -> None:
        """
        Print the progress bar for a stage that is about to begin.

        Args:
            stage_name  — Human-readable stage name.
            stage_index — 1-based stage index.
        """
        self._current = stage_index
        bar = self._render_bar(stage_index - 1)
        prefix = f"{_CYAN}{_BOLD}" if self._use_color else ""
        reset  = _RESET if self._use_color else ""
        print(
            f"\n{prefix}[{stage_index}/{self._total}]{reset} "
            f"{bar}  {stage_name}..."
        )

    def complete_stage(self, stage_name: str, elapsed: float) -> None:
        """
        Print completion status for a finished stage.

        Args:
            stage_name — Human-readable stage name.
            elapsed    — Time taken in seconds.
        """
        tick   = f"{_GREEN}✔{_RESET}" if self._use_color else "[OK]"
        print(f"  {tick} {stage_name} ({elapsed:.2f}s)")

    def print_summary(self, context: "BuildContext") -> None:
        """
        Print the final build summary after pipeline completion.

        Args:
            context — Completed BuildContext.
        """
        bar     = self._render_bar(self._total)
        elapsed = context.elapsed()
        status  = (
            f"{_GREEN}{_BOLD}SUCCESS{_RESET}"
            if self._use_color else "SUCCESS"
        )
        print(f"\n{bar}")
        print(f"  Build {status}  —  {context.build_id}")
        print(f"  Profile : {context.build_profile}")
        print(f"  Elapsed : {elapsed:.1f}s")
        print(f"  Stages  : {len(context.stage_log)}/{self._total} completed")
        if context.has_errors():
            err_label = f"{_YELLOW}Warnings{_RESET}" if self._use_color else "Warnings"
            print(f"  {err_label}: {len(context.errors)}")
        if context.artifacts:
            print("  Artifacts:")
            for key, path in context.artifacts.items():
                print(f"    {key}: {path}")
        print()

    # ---------------------------------------------------------------- #
    # Private helpers                                                   #
    # ---------------------------------------------------------------- #

    def _render_bar(self, completed: int) -> str:
        """Render a filled progress bar string."""
        filled = int(self.BAR_WIDTH * completed / self._total)
        empty  = self.BAR_WIDTH - filled
        bar    = _FILL * filled + _EMPTY * empty
        if self._use_color:
            pct    = int(100 * completed / self._total)
            return f"[{_GREEN}{bar}{_RESET}] {pct:3d}%"
        return f"[{bar}]"
