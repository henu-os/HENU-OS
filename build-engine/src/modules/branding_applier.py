from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class BrandingApplier:
    """
    Apply HENU OS user-facing branding to the live-build chroot.

    Debian upstream legal/copyright/license files are intentionally
    preserved. This module changes the visible operating-system identity.
    """

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = Path(workspace_root).resolve()
        self._logger = logger

    # ---------------------------------------------------------
    # Basic filesystem helpers
    # ---------------------------------------------------------

    def _copy_file(self, source: Path, destination: Path) -> None:
        if not source.is_file():
            raise RuntimeError(f"Branding asset not found: {source}")

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    def _extract_zip(self, source: Path, destination: Path) -> None:
        if not source.is_file():
            raise RuntimeError(f"Branding archive not found: {source}")

        destination.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(source, "r") as archive:
            archive.extractall(destination)

    def _find_first_file(
        self,
        root: Path,
        patterns: tuple[str, ...],
    ) -> Path | None:

        if not root.exists():
            return None

        for pattern in patterns:
            matches = list(root.rglob(pattern))
            if matches:
                return matches[0]

        return None

    def _copy_tree_contents(
        self,
        source: Path,
        destination: Path,
    ) -> None:

        destination.mkdir(parents=True, exist_ok=True)

        for item in source.iterdir():
            target = destination / item.name

            if item.is_dir():
                shutil.copytree(
                    item,
                    target,
                    dirs_exist_ok=True,
                )
            else:
                shutil.copy2(item, target)

    # ---------------------------------------------------------
    # OS identity
    # ---------------------------------------------------------

    def _write_os_identity(self, root: Path) -> None:

        etc = root / "etc"
        etc.mkdir(parents=True, exist_ok=True)

        os_release = """PRETTY_NAME="HENU OS 3.0"
NAME="HENU OS"
VERSION_ID="3.0"
VERSION="3.0.0-alpha.1 (Antigravity)"
VERSION_CODENAME="Antigravity"
ID=henu
ID_LIKE=debian
HOME_URL="https://henu-os.org"
SUPPORT_URL="https://henu-os.org/support"
BUG_REPORT_URL="https://henu-os.org/issues"
VARIANT="HENU OS"
VARIANT_ID="henu"
"""

        (etc / "os-release").write_text(
            os_release,
            encoding="utf-8",
        )

        (etc / "issue").write_text(
            "HENU OS 3.0 \\n \\l\n",
            encoding="utf-8",
        )

        (etc / "issue.net").write_text(
            "HENU OS 3.0\n",
            encoding="utf-8",
        )

        (etc / "motd").write_text(
            "\n"
            "========================================\n"
            "             HENU OS 3.0\n"
            "       Secure by Design. Built for Everyone.\n"
            "              Antigravity\n"
            "========================================\n"
            "\n",
            encoding="utf-8",
        )

    # ---------------------------------------------------------
    # HENU icons
    # ---------------------------------------------------------

    def _install_icons(self, root: Path) -> None:

        icon_source = (
            self._workspace /
            "branding" /
            "icons" /
            "henu.png"
        )

        if not icon_source.is_file():
            icon_source = (
                self._workspace /
                "branding" /
                "logos" /
                "primary" /
                "henu.png"
            )

        if not icon_source.is_file():
            raise RuntimeError(
                "Cannot find HENU primary icon/logo"
            )

        hicolor = (
            root /
            "usr" /
            "share" /
            "icons" /
            "hicolor"
        )

        for size in ("48x48", "64x64", "128x128", "256x256", "512x512"):

            destination = (
                hicolor /
                size /
                "apps" /
                "henu.png"
            )

            self._copy_file(
                icon_source,
                destination,
            )

        # Create a valid HENU icon theme which inherits
        # from standard GNOME icons.
        henu_theme = (
            root /
            "usr" /
            "share" /
            "icons" /
            "HENU-Icons"
        )

        henu_theme.mkdir(
            parents=True,
            exist_ok=True,
        )

        (henu_theme / "index.theme").write_text(
            """[Icon Theme]
Name=HENU Icons
Comment=HENU OS Icon Theme
Inherits=Adwaita,hicolor
Directories=48x48/apps,64x64/apps,128x128/apps,256x256/apps,512x512/apps

[48x48/apps]
Size=48
Context=Applications
Type=Fixed

[64x64/apps]
Size=64
Context=Applications
Type=Fixed

[128x128/apps]
Size=128
Context=Applications
Type=Fixed

[256x256/apps]
Size=256
Context=Applications
Type=Fixed

[512x512/apps]
Size=512
Context=Applications
Type=Fixed
""",
            encoding="utf-8",
        )

        for size in ("48x48", "64x64", "128x128", "256x256", "512x512"):

            destination = (
                henu_theme /
                size /
                "apps" /
                "henu.png"
            )

            self._copy_file(
                icon_source,
                destination,
            )

    # ---------------------------------------------------------
    # Wallpapers
    # ---------------------------------------------------------

    def _install_wallpapers(self, root: Path) -> None:

        wallpaper_root = (
            self._workspace /
            "branding" /
            "wallpapers"
        )

        destination = (
            root /
            "usr" /
            "share" /
            "backgrounds" /
            "henu"
        )

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        candidates = [
            wallpaper_root /
            "official" /
            "extra [no fix dimension]" /
            "wallpapers (30).png",

            wallpaper_root /
            "official" /
            "wallpapers (14).png",

            wallpaper_root /
            "official" /
            "fhd" /
            "1920×1080 (6).png",

            wallpaper_root /
            "lockscreen" /
            "lockscreen (3).png",

            wallpaper_root /
            "login" /
            "login (5).png",

            wallpaper_root /
            "plymouth" /
            "splash-background" /
            "1920 x 1080.png",

            wallpaper_root /
            "official" /
            "fhd" /
            "1920×1080 (17).png",
        ]

        copied = 0

        for source in candidates:

            if source.is_file():

                target = (
                    destination /
                    f"wallpaper-{copied + 1:02d}.png"
                )

                shutil.copy2(
                    source,
                    target,
                )

                copied += 1

        if copied == 0:
            raise RuntimeError(
                "No HENU wallpapers were found"
            )

        # First/default wallpaper
        first = destination / "wallpaper-01.png"

        default_target = (
            root /
            "usr" /
            "share" /
            "backgrounds" /
            "henu" /
            "henu-default.png"
        )

        shutil.copy2(
            first,
            default_target,
        )

    # ---------------------------------------------------------
    # GTK theme
    # ---------------------------------------------------------

    def _install_gtk_theme(self, root: Path) -> None:

        archive = (
            self._workspace /
            "branding" /
            "themes" /
            "Colloid-gtk-theme-main.zip"
        )

        if not archive.is_file():
            raise RuntimeError(
                f"Missing GTK theme archive: {archive}"
            )

        staging = (
            self._workspace /
            "build" /
            "work" /
            "branding-extract" /
            "gtk"
        )

        if staging.exists():
            shutil.rmtree(staging)

        self._extract_zip(
            archive,
            staging,
        )

        destination = (
            root /
            "usr" /
            "share" /
            "themes"
        )

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Copy theme directories while avoiding an extra
        # archive-root directory where possible.
        roots = [
            p for p in staging.iterdir()
            if p.is_dir()
        ]

        for item in roots:

            # If this directory contains actual theme directories,
            # copy them individually.
            children = [
                child for child in item.iterdir()
                if child.is_dir()
            ]

            theme_children = [
                child for child in children
                if (
                    (child / "gtk-3.0").exists()
                    or
                    (child / "gtk-4.0").exists()
                )
            ]

            if theme_children:

                for theme in theme_children:

                    shutil.copytree(
                        theme,
                        destination / theme.name,
                        dirs_exist_ok=True,
                    )

            elif (
                (item / "gtk-3.0").exists()
                or
                (item / "gtk-4.0").exists()
            ):

                shutil.copytree(
                    item,
                    destination / item.name,
                    dirs_exist_ok=True,
                )

    # ---------------------------------------------------------
    # Cursor
    # ---------------------------------------------------------

    def _install_cursor(self, root: Path) -> None:

        archive = (
            self._workspace /
            "branding" /
            "cursor" /
            "XCursor-pro-main.zip"
        )

        if not archive.is_file():
            raise RuntimeError(
                f"Missing cursor archive: {archive}"
            )

        staging = (
            self._workspace /
            "build" /
            "work" /
            "branding-extract" /
            "cursor"
        )

        if staging.exists():
            shutil.rmtree(staging)

        self._extract_zip(
            archive,
            staging,
        )

        destination = (
            root /
            "usr" /
            "share" /
            "icons"
        )

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        for directory in staging.rglob("cursors"):

            parent = directory.parent

            if parent.is_dir():

                shutil.copytree(
                    parent,
                    destination / parent.name,
                    dirs_exist_ok=True,
                )

    # ---------------------------------------------------------
    # Fonts
    # ---------------------------------------------------------

    def _install_fonts(self, root: Path) -> None:

        destination = (
            root /
            "usr" /
            "share" /
            "fonts" /
            "henu"
        )

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        archives = [
            self._workspace /
            "branding" /
            "fonts" /
            "Libertinus_Mono.zip",

            self._workspace /
            "branding" /
            "fonts" /
            "Revalia.zip",
        ]

        staging_base = (
            self._workspace /
            "build" /
            "work" /
            "branding-extract" /
            "fonts"
        )

        staging_base.mkdir(
            parents=True,
            exist_ok=True,
        )

        for archive in archives:

            if not archive.is_file():
                raise RuntimeError(
                    f"Missing font archive: {archive}"
                )

            staging = (
                staging_base /
                archive.stem
            )

            if staging.exists():
                shutil.rmtree(staging)

            self._extract_zip(
                archive,
                staging,
            )

            for font in staging.rglob("*"):

                if font.is_file() and font.suffix.lower() in {
                    ".ttf",
                    ".otf",
                    ".woff",
                    ".woff2",
                }:

                    shutil.copy2(
                        font,
                        destination / font.name,
                    )

    # ---------------------------------------------------------
    # GDM
    # ---------------------------------------------------------

    def _configure_gdm(self, root: Path) -> None:

        gdm = root / "etc" / "gdm3"

        gdm.mkdir(
            parents=True,
            exist_ok=True,
        )

        daemon = gdm / "daemon.conf"

        daemon.write_text(
            """[daemon]
WaylandEnable=true
AutomaticLoginEnable=false

[security]

[xdmcp]

[chooser]

[debug]
""",
            encoding="utf-8",
        )

        # GNOME GDM greeter dconf defaults
        dconf_dir = (
            gdm /
            "greeter.d"
        )

        dconf_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        defaults = dconf_dir / "01-henu-branding"

        defaults.write_text(
            """[org/gnome/desktop/background]
picture-uri='file:///usr/share/backgrounds/henu/henu-default.png'
picture-uri-dark='file:///usr/share/backgrounds/henu/henu-default.png'
picture-options='zoom'
primary-color='#0b0f19'
secondary-color='#0b0f19'

[org/gnome/desktop/interface]
color-scheme='prefer-dark'
cursor-theme='XCursor-pro'
icon-theme='HENU-Icons'
""",
            encoding="utf-8",
        )

        # Debian's normal greeter dconf location
        legacy = gdm / "greeter.dconf-defaults"

        legacy.write_text(
            """[org/gnome/desktop/background]
picture-uri='file:///usr/share/backgrounds/henu/henu-default.png'
picture-uri-dark='file:///usr/share/backgrounds/henu/henu-default.png'
picture-options='zoom'

[org/gnome/desktop/interface]
icon-theme='HENU-Icons'
cursor-theme='XCursor-pro'
color-scheme='prefer-dark'
""",
            encoding="utf-8",
        )

    # ---------------------------------------------------------
    # Plymouth
    # ---------------------------------------------------------

    def _install_plymouth(self, root: Path) -> None:

        archive = (
            self._workspace /
            "branding" /
            "plymouth" /
            "PlymouthTheme-Cat-master.zip"
        )

        if not archive.is_file():
            raise RuntimeError(
                f"Missing Plymouth archive: {archive}"
            )

        staging = (
            self._workspace /
            "build" /
            "work" /
            "branding-extract" /
            "plymouth"
        )

        if staging.exists():
            shutil.rmtree(staging)

        self._extract_zip(
            archive,
            staging,
        )

        destination = (
            root /
            "usr" /
            "share" /
            "plymouth" /
            "themes"
        )

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        for item in staging.rglob("*.plymouth"):

            theme_dir = item.parent

            if theme_dir.is_dir():

                target = destination / "henu"

                shutil.copytree(
                    theme_dir,
                    target,
                    dirs_exist_ok=True,
                )

                # Rename the actual Plymouth descriptor to HENU.
                descriptors = list(
                    target.glob("*.plymouth")
                )

                if descriptors:

                    original = descriptors[0]

                    renamed = target / "henu.plymouth"

                    if original != renamed:
                        shutil.copy2(
                            original,
                            renamed,
                        )

                break

        henu_theme = destination / "henu"

        if henu_theme.exists():

            default = root / "etc" / "default"

            default.mkdir(
                parents=True,
                exist_ok=True,
            )

            plymouth_conf = (
                default /
                "plymouth"
            )

            plymouth_conf.write_text(
                "PLYMOUTH_THEME_NAME=henu\n",
                encoding="utf-8",
            )

    # ---------------------------------------------------------
    # GRUB identity
    # ---------------------------------------------------------

    def _configure_grub_identity(self, root: Path) -> None:

        default = (
            root /
            "etc" /
            "default" /
            "grub"
        )

        default.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        existing = ""

        if default.exists():
            existing = default.read_text(
                encoding="utf-8",
                errors="ignore",
            )

        lines = [
            line for line in existing.splitlines()
            if not line.startswith("GRUB_DISTRIBUTOR=")
        ]

        lines.append(
            'GRUB_DISTRIBUTOR="HENU OS"'
        )

        lines.append(
            'GRUB_TIMEOUT_STYLE=menu'
        )

        lines.append(
            'GRUB_TIMEOUT=5'
        )

        lines.append(
            'GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"'
        )

        default.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

    # ---------------------------------------------------------
    # Calamares
    # ---------------------------------------------------------

    def _configure_calamares(self, root: Path) -> None:

        source = (
            self._workspace /
            "installer" /
            "calamares" /
            "branding" /
            "henu"
        )

        destination = (
            root /
            "etc" /
            "calamares" /
            "branding" /
            "henu"
        )

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        if source.is_dir():

            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True,
            )

        settings = (
            self._workspace /
            "installer" /
            "calamares" /
            "settings.conf"
        )

        if settings.is_file():

            target = (
                root /
                "etc" /
                "calamares" /
                "settings.conf"
            )

            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                settings,
                target,
            )

        # Make HENU logo available under common Calamares names.
        logo = (
            self._workspace /
            "branding" /
            "logos" /
            "primary" /
            "henu.png"
        )

        icon = (
            self._workspace /
            "branding" /
            "icons" /
            "henu.png"
        )

        if logo.is_file():

            self._copy_file(
                logo,
                destination / "logo.png",
            )

            self._copy_file(
                logo,
                destination / "welcome.png",
            )

        if icon.is_file():

            self._copy_file(
                icon,
                destination / "icon.png",
            )

    # ---------------------------------------------------------
    # Desktop defaults
    # ---------------------------------------------------------

    def _configure_desktop_defaults(self, root: Path) -> None:

        dconf = (
            root /
            "etc" /
            "dconf" /
            "db" /
            "local.d"
        )

        dconf.mkdir(
            parents=True,
            exist_ok=True,
        )

        profile = (
            root /
            "etc" /
            "dconf" /
            "profile"
        )

        profile.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not profile.exists():

            profile.write_text(
                "user-db:user\nsystem-db:local\n",
                encoding="utf-8",
            )

        defaults = (
            dconf /
            "01-henu"
        )

        defaults.write_text(
            """[org/gnome/desktop/interface]
gtk-theme='Colloid-Dark'
icon-theme='HENU-Icons'
cursor-theme='XCursor-pro'
monospace-font-name='Libertinus Mono 10'
font-name='Revalia 11'
color-scheme='prefer-dark'

[org/gnome/desktop/background]
picture-uri='file:///usr/share/backgrounds/henu/henu-default.png'
picture-uri-dark='file:///usr/share/backgrounds/henu/henu-default.png'
picture-options='zoom'

[org/gnome/shell]
favorite-apps=['firefox.desktop','org.gnome.Nautilus.desktop']
disable-user-extensions=false

[org/gnome/desktop/wm/preferences]
button-layout='appmenu:close'
""",
            encoding="utf-8",
        )

    # ---------------------------------------------------------
    # Desktop shortcut
    # ---------------------------------------------------------

    def _create_installer_launcher(self, root: Path) -> None:

        applications = (
            root /
            "usr" /
            "share" /
            "applications"
        )

        applications.mkdir(
            parents=True,
            exist_ok=True,
        )

        desktop = (
            applications /
            "install-henu-os.desktop"
        )

        desktop.write_text(
            """[Desktop Entry]
Name=Install HENU OS
Comment=Install HENU OS on this computer
Exec=calamares
Icon=henu
Terminal=false
Type=Application
Categories=System;
StartupNotify=true
""",
            encoding="utf-8",
        )

    # ---------------------------------------------------------
    # Main operation
    # ---------------------------------------------------------

    def apply_branding(
        self,
        context: BuildContext,
        target_rootfs: str,
    ) -> bool:

        root = Path(target_rootfs).resolve()

        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._logger.info(
            "Applying final HENU OS user-facing branding"
        )

        self._write_os_identity(root)
        self._install_icons(root)
        self._install_wallpapers(root)
        self._install_gtk_theme(root)
        self._install_cursor(root)
        self._install_fonts(root)
        self._configure_gdm(root)
        self._install_plymouth(root)
        self._configure_grub_identity(root)
        self._configure_calamares(root)
        self._configure_desktop_defaults(root)
        self._create_installer_launcher(root)

        context.metadata["branding"] = {
            "os_name": "HENU OS",
            "version": "3.0.0-alpha.1",
            "codename": "Antigravity",
            "user_facing_debian_branding_replaced": True,
            "debian_legal_files_preserved": True,
        }

        self._logger.info(
            "HENU OS branding successfully staged"
        )

        return True
