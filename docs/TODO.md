# HENU OS Developer TODO List

This document acts as a repository checklist for developers working on the build system, applications, and configurations.

---

## 🏃 Sprint 1 (Current Build System Initialization)
- [x] Create workspace directories structure.
- [x] Create core repo files (`README.md`, `LICENSE`, `.gitignore`).
- [x] Write design system and architecture documents.
- [x] Create skeleton scripts for build automation.
- [x] Initialize 12 applications under `apps/` with isolation files.

---

## 📅 Sprint 2 (Build Engine Automation - Completed)
- [x] Milestone 1: Created engineering rules [docs/HENU_ENGINEERING_RULES.md](file:///H:/HENU-os/HENU%20OS%203.0/HENU-OS/docs/HENU_ENGINEERING_RULES.md)
- [x] Milestone 2: Created split YAML configurations (`build`, `desktop`, `branding`, `package`, `release` configs)
- [x] Milestone 3: Created build-engine directory module skeleton (`src/core/` and `src/modules/`)
- [x] Milestone 4: Programmed Build Pipeline orchestrator interface (`pipeline.py`)
- [x] Milestone 5: Added multi-target logging module (`logging.py`) generating split logs
- [x] Milestone 6: Programmed environmental pre-flight check validation subsystem (`validator.py`)
- [x] Milestone 7: Created developer documentation including application specifications (`docs/apps/`)

---

## 🎨 Sprint 3 (Branding and Installation)
- [ ] Implement branding assets copy utilities.
- [ ] Create custom grub themes.
- [ ] Implement plymouth boot screen configuration settings.
- [ ] Set up desktop default settings using dconf/gsettings overrides.

---

## 🐚 Sprint 4 (Desktop & Custom Apps)
- [ ] Develop settings dashboard prototype.
- [ ] Develop custom terminal wrapper window.
- [ ] Integrate file explorer configurations.

---

## 🧠 Sprint 5 (Offline AI Stack)
- [ ] Set up Llama.cpp base libraries.
- [ ] Write local socket API to handle prompt requests safely.
- [ ] Establish permission prompts user UI.
