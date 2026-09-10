"""
HENU OS 3.0 — Build Engine
File: src/models/pipeline_stage.py
Purpose: Abstract base class defining the PipelineStage contract.
         Every pipeline stage (Read Config, Validate, Install Packages…)
         must inherit from PipelineStage and implement execute().

         Dependency Injection: stages receive ILogger and IConfiguration
         interfaces, never concrete classes, making them testable in isolation.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from src.models.build_context import BuildContext


# ------------------------------------------------------------------ #
# Interfaces (Dependency Injection contracts)                         #
# ------------------------------------------------------------------ #

class ILogger(ABC):
    """Interface contract for the logging service injected into stages."""

    @abstractmethod
    def info(self, message: str) -> None: ...

    @abstractmethod
    def warning(self, message: str) -> None: ...

    @abstractmethod
    def error(self, message: str) -> None: ...

    @abstractmethod
    def success(self, message: str) -> None: ...


class IConfiguration(ABC):
    """Interface contract for the configuration service injected into stages."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any: ...

    @abstractmethod
    def all(self) -> dict: ...


class IValidator(ABC):
    """Interface contract for the validator service injected into stages."""

    @abstractmethod
    def run_all_checks(self, config: dict) -> None: ...


class IPluginLoader(ABC):
    """Interface contract for the plugin loader injected into the pipeline."""

    @abstractmethod
    def fire_hook(self, hook_name: str, context: "BuildContext") -> None: ...


# ------------------------------------------------------------------ #
# Abstract Pipeline Stage                                             #
# ------------------------------------------------------------------ #

class PipelineStage(ABC):
    """
    Abstract base class for every build pipeline stage.

    Subclasses implement execute() which receives a BuildContext and
    returns the (potentially modified) BuildContext.

    Rollback:   Stages register a rollback callable before starting.
                On pipeline failure, RollbackManager calls these in reverse.
    Checkpoint: After successful execute(), the pipeline records stage
                name in CheckpointManager for resume-on-failure.
    """

    def __init__(self, name: str, logger: ILogger) -> None:
        self.name = name
        self.logger = logger
        self._rollback_fn: Optional[Callable[[], None]] = None

    def register_rollback(self, fn: Callable[[], None]) -> None:
        """Register a callable that undoes this stage's side effects."""
        self._rollback_fn = fn

    def rollback(self) -> None:
        """Execute the registered rollback function if one exists."""
        if self._rollback_fn:
            self.logger.warning(f"Rolling back stage: {self.name}")
            self._rollback_fn()

    def run(self, context: "BuildContext") -> "BuildContext":
        """
        Wraps execute() with timing and logging.
        Returns the modified BuildContext.
        """
        start = time.time()
        self.logger.info(f"Stage '{self.name}' starting...")
        result = self.execute(context)
        elapsed = round(time.time() - start, 2)
        self.logger.info(f"Stage '{self.name}' completed in {elapsed}s.")
        return result

    @abstractmethod
    def execute(self, context: "BuildContext") -> "BuildContext":
        """
        Stage-specific logic. Must read from context, do work,
        update context, and return it. Never use global variables.
        """
        ...
