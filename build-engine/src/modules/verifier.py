from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class BuildVerifier:
    """Perform real ISO validation."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = Path(workspace_root).resolve()
        self._logger = logger

    def verify_iso(self, context: BuildContext) -> bool:
        iso = context.get_artifact("iso")

        if not iso:
            raise RuntimeError("No ISO artifact registered.")

        path = Path(iso)

        if not path.is_file():
            raise RuntimeError(f"ISO does not exist: {path}")

        size = path.stat().st_size

        if size <= 1024 * 1024:
            raise RuntimeError(
                f"ISO is invalid or empty: {size} bytes"
            )

        xorriso = shutil.which("xorriso")

        if not xorriso:
            raise RuntimeError("xorriso is required for ISO verification.")

        result = subprocess.run(
            [xorriso, "-indev", str(path), "-toc"],
            text=True,
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "xorriso rejected the generated ISO."
            )

        context.metadata["iso_size_bytes"] = size
        context.metadata["iso_verified"] = True

        self._logger.success(
            f"ISO verified successfully: "
            f"{size / 1024 / 1024:.1f} MiB"
        )

        return True
