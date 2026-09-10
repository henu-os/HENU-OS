# HENU OS 3.0

> **Version: 3.0.0-alpha.1**  
> **Base OS: Debian GNU/Linux 13 (Trixie)**  
> **Status: Debian Build System & Build Engine Configured (Sprint 2 Complete)**  

Welcome to the official developer workspace for **HENU OS 3.0**. This project builds a modern, AI-integrated, and secure operating system on top of a Debian 13 (*Trixie*) base using Debian `live-build` and `debootstrap`.

---

## 📂 Folder Architecture

This workspace is structured cleanly to enforce separation of concerns, ensuring that the upstream Debian base is never modified directly. Every change passes through declarative configurations and automated pipelines:

```text
HENU-OS/
├── apps/               # Independent sub-applications (ai, ide, hub, etc.)
├── assets/             # Runtime media assets placeholders
├── branding/           # Active custom logos, GRUB, Plymouth, GDM3, and wallpapers
├── branding-package/   # Standalone Debian branding package (.deb) definitions
├── build/              # ISO build processes, APT caches, build logs, and outputs
├── build-engine/       # Python build pipeline, live-build templates, and validation
├── ci/                 # CI/CD pipeline automation workflows
├── configs/            # Split system configuration YAMLs (debian, branding, package, etc.)
├── desktop/            # Desktop environments, GNOME shell integrations, dconf
├── docs/               # Architecture specifications, changelogs, roadmaps, and TODOs
├── installer/          # Replaceable Calamares / Debian-Installer subsystem
├── kernel/             # Kernel configurations, patches, and build scripts
├── packages/           # Custom Debian packaging workspace (.deb)
├── release/            # Stable release files and distributions
├── scripts/            # Automated build, branding, and environment setup scripts
└── testing/            # Automated QEMU boot test suites and validation harnesses
```

---

## 🛠️ Design & Development Rules

1. **Never Manually Change Linux**: All customizations (branding, configuration, package installation) must be declared in `configs/` and automated via `build-engine/` and `live-build`.
2. **Debian Native Packaging**: All custom software and branding assets are packaged into standard `.deb` format.
3. **Independent Applications**: Every application inside `apps/` is structured as a standalone project with its own README, LICENSE, and source directory.
4. **Branching Strategy**: 
   - `main`: Production and stable release branch.
   - `develop`: Main development integration branch.
   - `feature/*`: Topic branches for specific features or components.
5. **Semantic Versioning**: All releases must adhere strictly to semver standards (e.g. `3.0.0-alpha.1`).

---

## 📖 Architecture & Documentation

To explore the architecture and roadmap of HENU OS 3.0, refer to:
- [docs/ARCHITECTURE.md](file:///H:/HENU-os/HENU%20OS%203.0/HENU-OS/docs/ARCHITECTURE.md)
- [docs/ROADMAP.md](file:///H:/HENU-os/HENU%20OS%203.0/HENU-OS/docs/ROADMAP.md)
- [docs/UPSTREAM.md](file:///H:/HENU-os/HENU%20OS%203.0/HENU-OS/docs/UPSTREAM.md)
- [docs/HENU_ENGINEERING_RULES.md](file:///H:/HENU-os/HENU%20OS%203.0/HENU-OS/docs/HENU_ENGINEERING_RULES.md)
- [ostree.md](file:///H:/HENU-os/HENU%20OS%203.0/HENU-OS/ostree.md)
# HENU-OS
