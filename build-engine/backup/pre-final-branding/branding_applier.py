from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class BrandingApplier:
    """Install HENU OS branding into a live-build chroot include tree."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = Path(workspace_root).resolve()
        self._logger = logger

    def _copy_file(self, source: Path, destination: Path) -> None:
        if not source.is_file():
            raise RuntimeError(f"Branding asset not found: {source}")

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    def _extract_zip(self, source: Path, destination: Path) -> None:
        if not source.is_file():
            raise RuntimeError(f"Branding archive not found: {source}")

        destination.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(source, "r") as zf:
            zf.extractall(destination)

    def apply_branding(
        self,
        context: BuildContext,
        target_rootfs: str,
    ) -> bool:
        cfg = context.config.get("branding", {})
        defaults = cfg.get("active_defaults", {})

        root = Path(target_rootfs).resolve()

        if not root.is_dir():
            raise RuntimeError(f"Branding target does not exist: {root}")

        backgrounds = root / "usr/share/backgrounds/henu"
        themes = root / "usr/share/themes"
        icons = root / "usr/share/icons"
        fonts = root / "usr/share/fonts/henu"
        sounds = root / "usr/share/sounds/henu"

        backgrounds.mkdir(parents=True, exist_ok=True)
        themes.mkdir(parents=True, exist_ok=True)
        icons.mkdir(parents=True, exist_ok=True)
        fonts.mkdir(parents=True, exist_ok=True)
        sounds.mkdir(parents=True, exist_ok=True)

        def asset(relative: str) -> Path:
            return self._workspace / relative

        # Core HENU logo.
        logo = asset(defaults.get(
            "logo_main",
            "branding/logos/primary/henu.png",
        ))

        self._copy_file(
            logo,
            icons / "henu.png",
        )

        # Selected wallpapers.
        wallpapers = [
            defaults.get("wallpaper_first_time_user"),
            defaults.get("wallpaper_dark_theme_default"),
            defaults.get("wallpaper_light_theme_default"),
            defaults.get("wallpaper_lockscreen"),
            defaults.get("wallpaper_login"),
        ]

        for index, wallpaper in enumerate(w for w in wallpapers if w):
            source = asset(wallpaper)
            self._copy_file(
                source,
                backgrounds / f"henu-wallpaper-{index + 1}.png",
            )

        # Selected GTK theme.
        gtk_zip = asset(defaults.get(
            "gtk_theme_source",
            "branding/themes/Colloid-gtk-theme-main.zip",
        ))

        self._extract_zip(gtk_zip, themes / ".henu-colloid")

        # Selected cursor theme.
        cursor_zip = asset(defaults.get(
            "cursor_theme_source",
            "branding/cursor/XCursor-pro-main.zip",
        ))

        self._extract_zip(cursor_zip, icons / ".henu-cursor")

        # Fonts.
        for font_zip in (
            defaults.get("font_primary_mono"),
            defaults.get("font_secondary_display"),
        ):
            if font_zip:
                self._extract_zip(
                    asset(font_zip),
                    fonts,
                )

        # Sounds.
        for name, source_path in defaults.get("sounds", {}).items():
            if source_path:
                self._copy_file(
                    asset(source_path),
                    sounds / Path(source_path).name,
                )

        # HENU identity.
        etc = root / "etc"
        etc.mkdir(parents=True, exist_ok=True)

        os_release = etc / "os-release"

        os_release.write_text(
            """NAME="HENU OS"
PRETTY_NAME="HENU OS 3.0"
ID=henu
ID_LIKE=debian
VERSION_ID="3.0"
VERSION="3.0.0-alpha.1"
VERSION_CODENAME="Antigravity"
HOME_URL="https://henu-os.org"
SUPPORT_URL="https://henu-os.org/support"
BUG_REPORT_URL="https://henu-os.org/issues"
""",
            encoding="utf-8",
        )

        (etc / "issue").write_text(
            "HENU OS 3.0 — Antigravity\\n",
            encoding="utf-8",
        )

        self._logger.success(
            "HENU OS branding assets and system identity prepared."
        )

        context.metadata["branding_applied"] = True
        return True
