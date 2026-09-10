# HENU OS Application Specification: henu-files

> **System Component: Core File Explorer**  
> **Package Identifier: henu-files**  
> **Status: Specification Draft**

---

## 1. Purpose
Provides a graphical file manager for exploring directory trees, viewing details, staging changes, and running permissions adjustments.

## 2. Features
- **Sidebar Shortcuts**: Home, Desktop, Downloads, Documents, System Root, Custom Mounts.
- **Search Engine**: Rapid indexed file querying.
- **Archive Extraction**: Zip, Tar, Gz, and DEB extractors context hooks.

## 3. Dependencies
- `gtk4`
- `tracker3` (indexing engine)
- `shared-mime-info`

## 4. Permissions
- **FileSystem**: Read/Write accesses based on POSIX user rights.
- **Devices**: Mount/Unmount storage hardware disks.

## 5. User Interface (UI)
Modern grid and list views with multi-tab layouts and context click dropdowns.

## 6. Future Roadmap
- Local network samba sharing configs.
- Secure folder lockers with passphrase encryption.
