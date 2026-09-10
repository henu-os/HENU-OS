# HENU OS 3.0 — Installer Subsystem

This subsystem provides the installation interfaces for **HENU OS 3.0**, designed as an independent and replaceable layer decoupled from live image generation.

## 📦 Supported Backends

1. **Calamares (Primary GUI Installer)**:
   - Modern, modular, and customizable Qt-based system installer.
   - Located in `installer/calamares/`.
   - Supports Btrfs subvolumes, LUKS encryption, user configuration, and HENU branding slides.

2. **Debian-Installer (D-I Preseed Fallback)**:
   - Standard Debian unattended installation configuration.
   - Located in `installer/debian-installer/preseed.cfg`.
   - Used for headless, automated enterprise, and OEM staging.
