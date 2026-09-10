# HENU OS Application Specification: henu-ide

> **System Component: Core Developer IDE**  
> **Package Identifier: henu-ide**  
> **Status: Specification Draft**

---

## 1. Purpose
Provides a native, lightning-fast development IDE designed for writing code, building Debian packages, and deploying system updates.

## 2. Features
- **Project Workspaces**: Standard sidebar tree viewer, terminal pane, split editor cards.
- **LSP Integrations**: Code linting and auto-complete for Bash, Python, and C/C++.
- **HENU Assistant Extension**: AI pair-programming panel linked to `henu-ai`.

## 3. Dependencies
- `gtksourceview5`
- `python3-lsp-server`
- `build-essential` / `dpkg-dev` / `debhelper` compiler kits

## 4. Permissions
- **FileSystem**: Read/Write accesses inside project root locations.
- **Process**: Spawn execution sub-commands (compilers, interpreters).
- **Socket**: Direct connection to `/run/henu-ai.sock`.

## 5. User Interface (UI)
Professional dark-themed multi-panel editor window featuring code coloring and tabs.

## 6. Future Roadmap
- Integrated Git visual staging graph.
- Remote development SSH bridges.
