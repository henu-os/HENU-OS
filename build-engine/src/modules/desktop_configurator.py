from __future__ import annotations

from pathlib import Path
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class DesktopConfigurator:
    """Configure GNOME defaults for HENU OS."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = Path(workspace_root).resolve()
        self._logger = logger

    def configure_desktop(
        self,
        context: BuildContext,
        target_rootfs: str,
    ) -> bool:
        root = Path(target_rootfs).resolve()

        dconf_dir = (
            root /
            "etc/dconf/db/local.d"
        )
        dconf_dir.mkdir(parents=True, exist_ok=True)

        desktop = context.config.get("desktop", {})

        theme = desktop.get("theme_name", "Colloid-Dark")
        icon_theme = desktop.get("icon_theme", "HENU-Icons")
        cursor_theme = desktop.get("cursor_theme", "XCursor-pro")
        font = desktop.get("font_name", "Inter 11")
        mono = desktop.get("mono_font_name", "Libertinus Mono 10")
        dark = desktop.get("dark_mode", True)

        wallpaper = (
            "/usr/share/backgrounds/henu/"
            "henu-wallpaper-1.png"
        )

        content = f"""[org/gnome/desktop/interface]
gtk-theme='{theme}'
icon-theme='{icon_theme}'
cursor-theme='{cursor_theme}'
font-name='{font}'
monospace-font-name='{mono}'
color-scheme='{'prefer-dark' if dark else 'default'}'

[org/gnome/desktop/background]
picture-uri='file://{wallpaper}'
picture-uri-dark='file://{wallpaper}'
picture-options='zoom'

[org/gnome/desktop/screensaver]
picture-uri='file://{wallpaper}'
"""

        (dconf_dir / "00-henu-defaults").write_text(
            content,
            encoding="utf-8",
        )

        profile_dir = root / "etc/dconf/profile"
        profile_dir.mkdir(parents=True, exist_ok=True)

        (profile_dir / "user").write_text(
            "user-db:user\nsystem-db:local\n",
            encoding="utf-8",
        )

        self._logger.success(
            f"GNOME HENU defaults configured: {theme}, "
            f"{cursor_theme}, {mono}"
        )

        context.metadata["desktop_configured"] = True
        return True
