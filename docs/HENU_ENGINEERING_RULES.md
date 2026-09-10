# HENU OS Engineering Rules (Constitution)

> **Version: 1.0.0**  
> **Status: Active**  
> **Applicability: All AI Assistants, Subagents, and Core Contributors**

This document establishes the strict engineering, architectural, coding, and security principles for the development of **HENU OS 3.0**. Every piece of code, configuration, or documentation generated for this project must adhere to these rules.

---

## 1. Directory and File Naming Rules

- **Folders**: Must be lowercase with hyphens or underscores (e.g. `build-engine/`, `branding-package/`). No spaces or capital letters in directory names unless explicitly mandated by third-party tooling.
- **Scripts**: 
  - Bash scripts must use `.sh` extensions (e.g. `bootstrap_build.sh`).
  - Python scripts must use `.py` extensions.
  - PowerShell scripts must use `.ps1` extensions.
- **Configurations**: Must use YAML (`.yaml` or `.yml`) or JSON (`.json`).
- **Documentation**: All developer-facing documentation must be written in Markdown (`.md`).

---

## 2. Coding Standards

### 2.1. Bash Scripts
- Every Bash script must begin with strict error checking:
  ```bash
  set -euo pipefail
  ```
- No hardcoded paths. Always derive directories relative to the script location:
  ```bash
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
  ```
- Every script must implement a standardized logging helper with severity prefixes:
  - `[INFO]`: System status notifications.
  - `[WARNING]`: Recoverable or non-fatal anomalies.
  - `[ERROR]`: Execution-stopping issues. Scripts must exit immediately on error.
- Use local variables (`local var_name`) inside functions to prevent scope leakage.

### 2.2. Python Code
- Must adere strictly to PEP 8 standards.
- Functions and methods must implement PEP 484 type hinting (e.g. `def parse_config(path: str) -> dict:`).
- Utilize structured exception handling (`try-except`) with precise exception classes rather than generic `except Exception`.
- Prefer native standard library modules (e.g. `pathlib`, `json`, `yaml` via PyYAML) to minimize runtime dependencies.

---

## 3. Architectural Modularity Rules

- **Debian Base Integrity**: Never manually modify live files inside the Debian base. All customizations must be applied as layers (packages, configurations, apps) by the **HENU Build Engine** via `live-build` and `debootstrap`.
- **Separation of Concerns**: The build toolchain logic must live entirely in `build-engine/`, completely separate from the core `configs/` and user space `apps/`.
- **Application Isolation**: Each application under `apps/` must be structured as an independent repository, containing:
  - A `src/` directory.
  - A `docs/` directory.
  - A `LICENSE` file.
  - A `.gitignore` file.
  - A `README.md` file.

---

## 4. Security Core Rules

- **Zero-Trust Defaults**: Ingress network connections must be blocked by default. Services should only listen on local interfaces unless explicitly configured.
- **AppArmor / MAC Compliance**: Security profiles must run in enforced mode. Custom applications requiring security privileges must declare them via AppArmor profiles.
- **Sandboxing**: Applications must operate within defined permission scopes (e.g., specifying file system, network, or AI socket access permissions in their manifest files).

---

## 5. Build and Package Standards

- **Bypass Caches**: When clean builds are specified, all intermediate compile folders, APT package caches, and old chroot systems must be completely wiped first to ensure build reproducibility.
- **Debian Packaging Specifications**: Custom packages and branding assets must be declared inside standard `debian/` directories (`control`, `rules`, `changelog`) and compiled into `.deb` format using `dpkg-deb` or `debuild` before being injected into the ISO. No raw files should be copied directly to system folders (`/usr/bin/`, etc.) without packaging.
- **ISO Replicability**: Any developer on a clean host must be able to run `bootstrap_build.sh` and generate an identical bootable ISO target, given the same input configurations.

---

## 6. Git Branching & Commits Rules

- **Commit Format**: Follow semantic commit formatting:
  - `feat(<component>):` for new features (e.g., `feat(build-engine): add configuration parser`).
  - `fix(<component>):` for bug fixes.
  - `docs(<component>):` for documentation adjustments.
  - `style(<component>):` for formatting corrections.
- **Branch Strategy**:
  - All feature work must take place on `feature/<sprint-number>-<name>` branches.
  - Integration occurs on `develop`.
  - Releases are tagged on `main`.

---

## 7. AI Code Generation Guidelines

- **No Placeholders**: Never generate `// TODO: implement later` or empty templates unless specifically requested to do so for scaffolding. Code must be production-ready and fully implemented.
- **Self-Documenting Code**: Code must contain clear inline comments explaining non-trivial logic, parameters, and algorithms.
- **Fail Fast**: Scripts must immediately halt and print human-readable debugging steps if a prerequisite check (like utility presence) fails.
