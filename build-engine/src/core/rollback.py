"""
HENU OS 3.0 — Build Engine
File: src/core/rollback.py
Purpose: Reverse rollback execution manager.
         Each pipeline stage registers a rollback callable before executing.
         On critical failure, RollbackManager walks backwards through
         registered rollbacks and executes them in LIFO order.

         This ensures partial build artifacts (mounted chroots, partial
         ISO directories) are cleaned up before the process exits.

Usage:
    rm = RollbackManager(logger)
    rm.register("Install Packages", lambda: shutil.rmtree(pkgs_dir))
    rm.execute_all()  # Called on pipeline failure.
"""

from __future__ import annotations

from typing import Callable, List, Tuple, Any


class RollbackManager:
    """
    LIFO (Last-In, First-Out) rollback executor.

    Stages register a cleanup callable before beginning work.
    On critical failure, the pipeline calls execute_all() to run
    all registered rollbacks in reverse registration order.

    Rollback callables must:
        - Accept no arguments.
        - Be idempotent (safe to call even if the stage partially failed).
        - Not raise unhandled exceptions.
    """

    def __init__(self, logger: Any) -> None:
        self._logger = logger
        self._stack:  List[Tuple[str, Callable[[], None]]] = []

    def register(self, stage_name: str, fn: Callable[[], None]) -> None:
        """
        Register a rollback callable for a pipeline stage.

        Args:
            stage_name — Human-readable stage name for logging.
            fn         — Zero-argument callable that undoes stage side effects.
        """
        self._stack.append((stage_name, fn))

    def execute_all(self) -> None:
        """
        Execute all registered rollbacks in reverse order (LIFO).
        Exceptions in individual rollbacks are caught and logged,
        ensuring all rollbacks are attempted even if one fails.
        """
        if not self._stack:
            self._logger.info("No rollback operations registered.")
            return

        self._logger.warning("Executing rollback sequence...")

        for stage_name, fn in reversed(self._stack):
            try:
                self._logger.warning(f"Rolling back: {stage_name}")
                fn()
                self._logger.info(f"Rollback complete: {stage_name}")
            except Exception as exc:
                self._logger.error(
                    f"Rollback for '{stage_name}' raised an error: {exc}"
                )

        self._logger.info("Rollback sequence finished.")

    def clear(self) -> None:
        """Clear all registered rollbacks. Call on successful pipeline completion."""
        self._stack.clear()

    @property
    def depth(self) -> int:
        """Number of registered rollback operations."""
        return len(self._stack)
