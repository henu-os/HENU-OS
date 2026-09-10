# Changelog

All notable changes to the **HENU OS 3.0** project will be documented in this file. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0-alpha.1] - 2026-07-20

### Added
- Milestone 1: Established the OS developer constitution [docs/HENU_ENGINEERING_RULES.md](file:///H:/HENU-os/HENU%20OS%203.0/HENU-OS/docs/HENU_ENGINEERING_RULES.md).
- Milestone 2: Reorganized configuration settings into split, indexable configuration files inside `configs/`:
  - `build_config.yaml`
  - `desktop_config.yaml`
  - `branding_config.yaml`
  - `package_config.yaml`
  - `release_config.yaml`
- Milestone 3: Reorganized `build-engine/` code modules using the `src/core/` and `src/modules/` directory hierarchy.
- Milestone 4: Configured class interfaces representing the 10 stages of the Build Pipeline inside `build-engine/src/core/pipeline.py`.
- Milestone 5: Implemented custom logging system inside `build-engine/src/core/logging.py` splitting output logs to `build.log`, `branding.log`, `packages.log`, `installer.log`, and `errors.log`.
- Milestone 6: Programmed the validation engine in `build-engine/src/core/validator.py` executing checks for disk space, folders structure, split configs, binary tools, and root admin rights.
- Milestone 7: Added developer documentation including the 13 application specifications under `docs/apps/`.

## [3.0.0-alpha.0] - 2026-07-20

### Added
- Created the project directory structure as specified in the Folder Architecture.
- Created root-level Git files: `README.md`, `.gitignore`, and `LICENSE`.
- Initialized core project documentation:
  - `docs/ARCHITECTURE.md` - Design and pipeline layout specifications.
  - `docs/ROADMAP.md` - Sprint breakdown planning.
  - `docs/TODO.md` - Developer task checklist.
  - `docs/README.md` - Docs directory index.
- Added template build configurations (`configs/build_config.yaml`).
- Added skeleton scripts for build execution and branding injection:
  - `scripts/build/bootstrap_build.sh`
  - `scripts/branding/apply_branding.sh`
  - `scripts/utilities/init_apps.sh`
- Set up structure for the 12 application workspaces inside `apps/` with independent Git repo attributes (README, LICENSE, gitignore, docs, src).
