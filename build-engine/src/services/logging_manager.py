"""
HENU OS 3.0 — Build Engine
File: src/services/logging_manager.py
Purpose: Central logging service implementing the ILogger interface.
         Provides three output channels:
           - Console   : colorized, human-readable
           - File      : date-structured plain text files
           - JSON      : structured key-value pairs for CI collectors

         Log files are organized by date:
           build-engine/logs/YYYY/MM/DD/<component>.log

         Every log entry includes:
           timestamp | module | level | thread_id | duration_ms | message

Dependencies:
    Python standard library: logging, threading, datetime, json, os.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, Optional

from src.models.pipeline_stage import ILogger


# ------------------------------------------------------------------ #
# Custom log level: SUCCESS                                           #
# ------------------------------------------------------------------ #

SUCCESS_LEVEL = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


# ------------------------------------------------------------------ #
# ANSI Color Codes for Console Output                                 #
# ------------------------------------------------------------------ #

class _Colors:
    RESET   = "\033[0m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD    = "\033[1m"


# ------------------------------------------------------------------ #
# Formatters                                                          #
# ------------------------------------------------------------------ #

class _ConsoleFormatter(logging.Formatter):
    """Colorized console formatter with level-specific color codes."""

    _LEVEL_COLORS: Dict[int, str] = {
        logging.DEBUG:   _Colors.CYAN,
        logging.INFO:    _Colors.BOLD,
        SUCCESS_LEVEL:   _Colors.GREEN,
        logging.WARNING: _Colors.YELLOW,
        logging.ERROR:   _Colors.RED,
        logging.CRITICAL: _Colors.RED + _Colors.BOLD,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self._LEVEL_COLORS.get(record.levelno, _Colors.RESET)
        level = f"{color}[{record.levelname}]{_Colors.RESET}"
        module = f"({os.path.basename(record.pathname)}:{record.lineno})"
        return f"{level} {module} {record.getMessage()}"


class _FileFormatter(logging.Formatter):
    """Plain timestamped file formatter with full context per entry."""

    def format(self, record: logging.LogRecord) -> str:
        ts      = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S,%f"
        )[:-3]  # millisecond precision
        level   = record.levelname
        module  = f"{os.path.basename(record.pathname)}:{record.lineno}"
        tid     = threading.current_thread().ident or 0
        # duration_ms: set by LoggingManager.timed_block or 0
        dur_ms  = getattr(record, "duration_ms", 0)
        return (
            f"{ts} [{level}] ({module}) "
            f"[TID:{tid}] [{dur_ms}ms] - {record.getMessage()}"
        )


class _JsonFormatter(logging.Formatter):
    """Structured JSON formatter for CI artifact collection."""

    def format(self, record: logging.LogRecord) -> str:
        tid = threading.current_thread().ident or 0
        payload = {
            "timestamp":   datetime.fromtimestamp(record.created).isoformat(),
            "level":       record.levelname,
            "module":      record.pathname,
            "line":        record.lineno,
            "thread_id":   tid,
            "duration_ms": getattr(record, "duration_ms", 0),
            "message":     record.getMessage(),
        }
        return json.dumps(payload, ensure_ascii=False)


# ------------------------------------------------------------------ #
# LoggingManager                                                      #
# ------------------------------------------------------------------ #

class LoggingManager(ILogger):
    """
    Central logging service for the HENU Build Engine.

    Implements ILogger for Dependency Injection into pipeline stages.

    Channels:
        console  — Always active. Colorized stdout output.
        file     — Date-structured log files. One file per component.
        json     — Optional. Activated by engine_config.yaml → logging.json_output.

    Log directory structure:
        build-engine/logs/YYYY/MM/DD/
            build.log
            errors.log
            packages.log
            branding.log
            installer.log
            performance.log
            security.log

    Usage:
        log = LoggingManager(log_root, json_output=False)
        log.info("Stage started.")
        log.success("Build complete.")
        log.error("Validation failed.")
    """

    _COMPONENT_LOGGERS = [
        "build", "errors", "packages", "branding",
        "installer", "performance", "security",
    ]

    def __init__(
        self,
        log_root: str,
        json_output: bool = False,
        component: str = "build",
    ) -> None:
        self._log_root    = os.path.abspath(log_root)
        self._json_output = json_output
        self._component   = component
        self._start_time  = time.time()

        today = datetime.now().strftime("%Y/%m/%d")
        self._log_dir = os.path.join(self._log_root, today)
        os.makedirs(self._log_dir, exist_ok=True)

        self._logger   = self._build_logger(component)
        self._err_log  = self._get_error_handler()

    # ---------------------------------------------------------------- #
    # ILogger interface                                                  #
    # ---------------------------------------------------------------- #

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)
        self._err_log.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)
        self._err_log.error(message)

    def success(self, message: str) -> None:
        self._logger.log(SUCCESS_LEVEL, message)

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def critical(self, message: str) -> None:
        self._logger.critical(message)
        self._err_log.critical(message)

    # ---------------------------------------------------------------- #
    # Named component loggers                                           #
    # ---------------------------------------------------------------- #

    def get_component_logger(self, name: str) -> "LoggingManager":
        """
        Return a LoggingManager instance writing to a specific component log.

        Args:
            name — One of: 'packages', 'branding', 'installer',
                           'performance', 'security'.
        """
        return LoggingManager(self._log_root, self._json_output, name)

    # ---------------------------------------------------------------- #
    # Private builder methods                                           #
    # ---------------------------------------------------------------- #

    def _build_logger(self, component: str) -> logging.Logger:
        """Construct and configure the named logger for a component."""
        logger = logging.getLogger(f"henu.{component}")
        logger.setLevel(logging.DEBUG)

        if logger.handlers:
            return logger  # Prevent duplicate handlers on re-init.

        # Console handler — use utf-8 reconfigure to prevent Windows cp1252 crashes.
        import sys
        import io
        try:
            # Python 3.7+: reconfigure stdout to UTF-8 if possible.
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            console_stream = sys.stdout
        except Exception:
            console_stream = sys.stdout
        ch = logging.StreamHandler(stream=console_stream)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(_ConsoleFormatter())
        logger.addHandler(ch)

        # File handler — component-specific log.
        log_path = os.path.join(self._log_dir, f"{component}.log")
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(
            _JsonFormatter() if self._json_output else _FileFormatter()
        )
        logger.addHandler(fh)

        return logger

    def _get_error_handler(self) -> logging.Logger:
        """
        Returns the centralised error logger that collects all
        WARNING+ messages from every component into errors.log.
        """
        err_logger = logging.getLogger("henu.errors")
        if err_logger.handlers:
            return err_logger

        err_logger.setLevel(logging.WARNING)
        err_path = os.path.join(self._log_dir, "errors.log")
        efh = logging.FileHandler(err_path, encoding="utf-8")
        efh.setLevel(logging.WARNING)
        efh.setFormatter(_FileFormatter())
        err_logger.addHandler(efh)
        return err_logger

    @property
    def log_dir(self) -> str:
        """Absolute path to today's log directory."""
        return self._log_dir
