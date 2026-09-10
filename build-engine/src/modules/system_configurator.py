from __future__ import annotations

from pathlib import Path
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class SystemConfigurator:
    """Configure HENU OS system identity and basic defaults."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = Path(workspace_root).resolve()
        self._logger = logger

    def apply_system_configuration(
        self,
        context: BuildContext,
        target_rootfs: str,
    ) -> bool:
        root = Path(target_rootfs).resolve()

        etc = root / "etc"
        etc.mkdir(parents=True, exist_ok=True)

        (etc / "hostname").write_text(
            "henu-os\n",
            encoding="utf-8",
        )

        locale_dir = etc / "default"
        locale_dir.mkdir(parents=True, exist_ok=True)

        (locale_dir / "locale").write_text(
            'LANG="en_US.UTF-8"\n'
            'LANGUAGE="en_US:en"\n',
            encoding="utf-8",
        )

        (etc / "timezone").write_text(
            "UTC\n",
            encoding="utf-8",
        )

        self._logger.success(
            "HENU OS system identity, locale and timezone configured."
        )

        context.metadata["system_configured"] = True
        return True
