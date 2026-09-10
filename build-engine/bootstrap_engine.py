#!/usr/bin/env python3
"""
HENU OS 3.0 — Build Engine
File: bootstrap_engine.py
Purpose: Single user-facing entry point for the HENU Build Engine CLI.

         Responsibilities:
           1. Verify Python minimum version (3.8+).
           2. Resolve absolute paths for the engine root and workspace root.
           3. Insert engine root into sys.path for clean src.* imports.
           4. Delegate to src.core.main.main() with the engine root.

Usage:
    python bootstrap_engine.py build
    python bootstrap_engine.py build --profile release --resume
    python bootstrap_engine.py validate
    python bootstrap_engine.py validate --profile testing
    python bootstrap_engine.py clean
    python bootstrap_engine.py doctor
    python bootstrap_engine.py plugin list

    # JSON log output for CI:
    python bootstrap_engine.py --json-logs build --profile release
"""

import os
import sys

# ------------------------------------------------------------------ #
# Minimum Python version guard                                        #
# ------------------------------------------------------------------ #

_MIN_PYTHON = (3, 8)

if sys.version_info < _MIN_PYTHON:
    print(
        f"[ERROR] HENU Build Engine requires Python "
        f"{'.'.join(map(str, _MIN_PYTHON))} or newer.\n"
        f"        Current: {sys.version}",
        file=sys.stderr,
    )
    sys.exit(1)

# ------------------------------------------------------------------ #
# Path resolution                                                     #
# ------------------------------------------------------------------ #

# engine_root = the build-engine/ directory (where this file lives).
ENGINE_ROOT = os.path.abspath(os.path.dirname(__file__))

# Insert engine root so that 'from src.core.xxx import ...' resolves.
if ENGINE_ROOT not in sys.path:
    sys.path.insert(0, ENGINE_ROOT)

# ------------------------------------------------------------------ #
# Entry                                                               #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    from src.core.main import main
    exit_code = main(ENGINE_ROOT)
    sys.exit(exit_code)
