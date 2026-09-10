from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class LiveBuildManager:
    """Prepare and execute a real Debian 13 Trixie live-build."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = Path(workspace_root).resolve()
        self._logger = logger

    def configure_live_system(
        self,
        context: BuildContext,
        live_dir: str,
    ) -> bool:
        live = Path(live_dir).resolve()
        live.mkdir(parents=True, exist_ok=True)

        template_root = (
            self._workspace /
            "build-engine" /
            "templates" /
            "live-build"
        )

        if not template_root.is_dir():
            raise RuntimeError(f"Missing live-build template: {template_root}")

        # Copy the complete existing live-build template.
        config_src = template_root / "config"
        config_dst = live / "config"

        if config_src.exists():
            shutil.copytree(config_src, config_dst, dirs_exist_ok=True)

        auto_src = template_root / "auto"
        auto_dst = live / "auto"

        if auto_src.exists():
            shutil.copytree(auto_src, auto_dst, dirs_exist_ok=True)

        auto_config = auto_dst / "config"

        if not auto_config.is_file():
            raise RuntimeError(f"Missing live-build auto/config: {auto_config}")

        os.chmod(auto_config, 0o755)

        # Generate package list from the merged HENU configuration.
        package_groups = context.config.get("package_groups", {})
        packages: list[str] = []

        for group in package_groups.values():
            if isinstance(group, list):
                packages.extend(str(p).strip() for p in group if str(p).strip())

        # Always include the packages required for a usable HENU GNOME live ISO.
        required = [
            "live-boot",
            "live-config",
            "live-config-systemd",
            "systemd-sysv",
            "gnome-core",
            "gnome-shell",
            "gdm3",
            "gnome-terminal",
            "nautilus",
            "network-manager-gnome",
            "pipewire",
            "pipewire-pulse",
            "wireplumber",
            "dconf-cli",
            "dconf-gsettings-backend",
            "calamares",
            "grub-efi-amd64",
            "os-prober",
            "plymouth",
            "plymouth-themes",
            "locales",
            "sudo",
            "ca-certificates",
        ]

        packages.extend(required)
        packages = sorted(set(packages))

        package_dir = config_dst / "package-lists"
        package_dir.mkdir(parents=True, exist_ok=True)

        package_file = package_dir / "henu.list.chroot"

        with package_file.open("w", encoding="utf-8") as f:
            f.write("# HENU OS 3.0 generated package list\n")
            f.write("# Debian 13 Trixie / amd64\n\n")
            for package in packages:
                f.write(package + "\n")

        self._logger.info(
            f"Generated HENU live-build package list: {len(packages)} packages"
        )

        # Ensure the branding hook is executable.
        hook_dir = config_dst / "hooks" / "live"
        hook_dir.mkdir(parents=True, exist_ok=True)

        for hook in hook_dir.glob("*.hook.chroot"):
            hook.chmod(0o755)

        # Record build information for later stages.
        context.metadata["live_build_dir"] = str(live)
        context.metadata["package_count"] = len(packages)

        self._logger.info("Running real live-build configuration...")

        result = subprocess.run(
            ["/bin/sh", str(auto_config)],
            cwd=str(live),
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"live-build configuration failed with exit code "
                f"{result.returncode}"
            )

        if not (live / "config").is_dir():
            raise RuntimeError(
                "live-build configuration finished but config/ is missing"
            )

        self._logger.success(
            f"Live-build workspace configured: {live}"
        )
        return True

    def build(self, context: BuildContext, live_dir: str) -> str:
        live = Path(live_dir).resolve()
        lb = shutil.which("lb") or "/usr/bin/lb"

        if not os.path.isfile(lb):
            raise RuntimeError("live-build (lb) not found")

        self._logger.info(
            "Starting REAL Debian live-build. "
            "This will download and assemble the operating system."
        )

        result = subprocess.run(
            [lb, "build"],
            cwd=str(live),
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"live-build failed with exit code {result.returncode}"
            )

        candidates = [
            live / "live-image-amd64.hybrid.iso",
            live / "live-image-amd64.iso",
        ]

        iso = next(
            (
                candidate
                for candidate in candidates
                if candidate.is_file()
                and candidate.stat().st_size > 1024 * 1024
            ),
            None,
        )

        if iso is None:
            raise RuntimeError(
                "live-build returned success but did not create a valid ISO"
            )

        context.metadata["live_build_iso"] = str(iso)

        self._logger.success(
            f"REAL ISO produced: {iso} "
            f"({iso.stat().st_size / 1024 / 1024:.1f} MiB)"
        )

        return str(iso)
