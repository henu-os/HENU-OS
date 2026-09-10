# HENU OS Application Specification: henu-sdk

> **System Component: Developer APIs & Software Development Kit**  
> **Package Identifier: henu-sdk**  
> **Status: Specification Draft**

---

## 1. Purpose
Provides system libraries, API definitions, and compilation wrappers enabling third-party developers to integrate their applications with HENU OS UI widgets, security permissions brokers, and local AI engines.

## 2. Features
- **UI Styling bindings**: Custom widget widgets styling variables.
- **AI Socket clients**: Pre-built clients for Python and C++ connecting to `henu-ai`.
- **Sandbox Manifest schemas**: Standard configuration templates defining permissions tags.

## 3. Dependencies
- `python3-devel`
- `glib2-devel`
- `gobject-introspection`

## 4. Permissions
- **System**: None (exposes SDK headers and static library libraries only).

## 5. User Interface (UI)
None (Developer SDK). Documentation maps are available inside [docs/](file:///H:/HENU-os/HENU%20OS%203.0/HENU-OS/docs/).

## 6. Future Roadmap
- Package templates for rapid app boilerplate initialization.
- Integration tests mock wrappers.
