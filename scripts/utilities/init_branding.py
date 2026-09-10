"""
HENU OS 3.0 — Branding Directory Initializer
Creates the complete branding folder structure with .gitkeep placeholders.
"""

import os

BASE = r"H:\HENU-os\HENU OS 3.0\HENU-OS\branding"

DIRS = [
    # Logos
    r"logos\primary",
    r"logos\secondary",
    r"logos\wordmark",
    r"logos\monochrome",
    r"logos\svg",
    r"logos\png",

    # Wallpapers
    r"wallpapers\official\4k",
    r"wallpapers\official\2k",
    r"wallpapers\official\fhd",
    r"wallpapers\login",
    r"wallpapers\lockscreen",
    r"wallpapers\installer",
    r"wallpapers\grub",
    r"wallpapers\plymouth",

    # Design assets
    "icons",
    "fonts",
    "themes",
    "sounds",
    "animations",
    "cursor",

    # System components
    "grub",
    "plymouth",
    "gdm",
    "installer",
]

created = 0
for d in DIRS:
    full = os.path.join(BASE, d)
    os.makedirs(full, exist_ok=True)
    gk = os.path.join(full, ".gitkeep")
    if not os.path.exists(gk):
        open(gk, "w").close()
    created += 1
    print(f"  [OK] branding/{d}")

print(f"\nBranding structure initialized: {created} directories.")
