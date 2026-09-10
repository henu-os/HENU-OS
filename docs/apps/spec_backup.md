# HENU OS Application Specification: henu-backup

> **System Component: Backup & Restore Manager**  
> **Package Identifier: henu-backup**  
> **Status: Specification Draft**

---

## 1. Purpose
Handles file system snapshots, user directory backups, and incremental replication scheduling to local or remote storage drives.

## 2. Features
- **Btrfs Snapshotting**: Atomic local volume backups.
- **Rsync Replication**: Directory structures mirroring to USB storage devices.
- **Cron Scheduling**: Daily/Weekly backup tasks automation.

## 3. Dependencies
- `btrfs-progs`
- `rsync`
- `tar`

## 4. Permissions
- **Admin**: root privileges required to capture raw block system snapshots.
- **Hardware**: Mount / Write access to storage volumes.
- **FileSystem**: Read rights across all backup targets.

## 5. User Interface (UI)
Simple timeline chart representing past backups, configuration dashboard for sources/destinations, and manual "Restore" trigger cards.

## 6. Future Roadmap
- Encryption support for backup sets.
- Network storage target support (NFS/SMB).
