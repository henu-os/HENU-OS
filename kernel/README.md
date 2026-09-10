# HENU OS 3.0 — Kernel Subsystem

This directory manages kernel strategy, custom patches, configurations, and out-of-tree module builds for **HENU OS 3.0**.

## 🌲 Strategy

1. **Initial Milestone (Sprint 2 & 3)**:
   - Uses official Debian 13 (`linux-image-amd64`) packages directly from `deb.debian.org`.
   - Guarantees upstream security updates, LTS stability, and broad hardware compatibility.

2. **Future Custom Kernel Milestones (Sprint 5+)**:
   - `config/`: Custom Linux kernel `.config` files.
   - `patches/`: Performance and scheduler tuning patches.
   - `modules/`: Out-of-tree hardware enablement drivers and DKMS definitions.
   - `scripts/build_kernel.sh`: Automated `make deb-pkg` compilation into native Debian `.deb` packages.
