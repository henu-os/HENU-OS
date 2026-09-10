# HENU OS Application Specification: henu-hub

> **System Component: Application Store & System Portal**  
> **Package Identifier: henu-hub**  
> **Status: Specification Draft**

---

## 1. Purpose
Provides a graphical user interface for finding, installing, updating, and removing custom HENU OS applications and upstream Debian packages.

## 2. Features
- **Visual App Store Interface**: Categorized listing of local applications (Developer, Cyber, Utilities, Desktop Apps).
- **Package Manager Wrapper**: Interfaces with APT and flatpak APIs for atomic installation.
- **Update Checker**: Automated background checks for transactional system upgrades.

## 3. Dependencies
- `flatpak`
- `apt` / PackageKit bindings (`python3-apt`)
- `libadwaita` GTK libraries

## 4. Permissions
- **Network**: Internet access required to check repositories.
- **FileSystem**: Read/Write access to `/etc/apt/sources.list.d/` and package download cache paths.
- **Privileges**: Root execution via Polkit prompts for installations.

## 5. User Interface (UI)
GTK4 / Libadwaita window with a sidebar navigator, app detail pages, and download status bars.

## 6. Future Roadmap
- Sandbox permissions toggle switches inside the store view.
- User review feedback loops.
