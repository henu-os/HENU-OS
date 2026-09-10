from __future__ import annotations

import shutil
from pathlib import Path
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class ISOBuilder:
    """Move the real live-build ISO into the HENU release directory."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = Path(workspace_root).resolve()
        self._logger = logger

    def build_iso(self, context: BuildContext) -> str:
        release = context.config.get("release", {})

        iso_name = release.get(
            "iso_name",
            "henu-os-3.0.0-alpha.1-amd64.iso",
        )

        source = context.metadata.get("live_build_iso")

        if not source:
            raise RuntimeError(
                "Live-build did not register a generated ISO."
            )

        source_path = Path(source)

        if not source_path.is_file():
            raise RuntimeError(
                f"Live-build ISO does not exist: {source_path}"
            )

        output_dir = self._workspace / "build/iso"
        output_dir.mkdir(parents=True, exist_ok=True)

        destination = output_dir / iso_name

        shutil.copy2(source_path, destination)

        if destination.stat().st_size <= 1024 * 1024:
            raise RuntimeError(
                "Copied ISO is smaller than 1 MiB."
            )

        context.set_artifact("iso", str(destination))

        self._logger.success(
            f"HENU OS ISO ready: {destination}"
        )

        return str(destination)
