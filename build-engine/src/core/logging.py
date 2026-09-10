# Logging Core Module for HENU Build Engine
# Version: 3.0.0-alpha.1

import os
import sys
import logging
from typing import Dict

class ConsoleFormatter(logging.Formatter):
    """Colorized console formatting helper."""
    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    NC = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        msg = record.getMessage()
        if level == "INFO":
            return f"{self.BLUE}[INFO]{self.NC} {msg}"
        elif level == "WARNING":
            return f"{self.YELLOW}[WARNING]{self.NC} {msg}"
        elif level == "ERROR" or level == "CRITICAL":
            return f"{self.RED}[ERROR]{self.NC} {msg}"
        elif level == "SUCCESS":
            return f"{self.GREEN}[SUCCESS]{self.NC} {msg}"
        return f"[{level}] {msg}"

# Add custom SUCCESS log level
logging.SUCCESS = 25 # type: ignore
logging.addLevelName(logging.SUCCESS, "SUCCESS")

def log_success(self, message: str, *args, **kws) -> None:
    if self.isEnabledFor(logging.SUCCESS):
        self._log(logging.SUCCESS, message, args, **kws)

logging.Logger.success = log_success # type: ignore

# Global registry of file handlers to close them cleanly later
_handlers: Dict[str, logging.FileHandler] = {}

def get_engine_logger(name: str = "build") -> logging.Logger:
    """Retrieves or creates a named logger (e.g. build, branding, packages, installer)."""
    return logging.getLogger(f"henu_{name}")

def init_logging_system(log_dir: str) -> None:
    """Sets up the split logger handlers writing to dedicated log files."""
    os.makedirs(log_dir, exist_ok=True)
    
    # Common file formatter
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s")
    
    # 1. Base log configuration (errors.log)
    # The errors.log captures warnings, errors, and critical messages from all modules.
    errors_filepath = os.path.join(log_dir, "errors.log")
    errors_handler = logging.FileHandler(errors_filepath, encoding="utf-8")
    errors_handler.setLevel(logging.WARNING)
    errors_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ConsoleFormatter())

    # Map engine components to dedicated file targets
    targets = {
        "build": "build.log",
        "branding": "branding.log",
        "packages": "packages.log",
        "installer": "installer.log"
    }

    for name, filename in targets.items():
        logger = logging.getLogger(f"henu_{name}")
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplication
        if logger.handlers:
            continue

        # File target handler
        filepath = os.path.join(log_dir, filename)
        f_handler = logging.FileHandler(filepath, encoding="utf-8")
        f_handler.setLevel(logging.DEBUG)
        f_handler.setFormatter(file_formatter)
        
        logger.addHandler(f_handler)
        logger.addHandler(errors_handler)
        logger.addHandler(console_handler)
        
        _handlers[name] = f_handler

    logging.getLogger("henu_build").info(f"Split logging initialized under directory: {log_dir}")
