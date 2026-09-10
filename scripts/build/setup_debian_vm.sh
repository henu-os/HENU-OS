#!/usr/bin/env bash
# ==============================================================================
# HENU OS 3.0 — Debian 13 Development VM Dependency Installer
# Purpose: Installs all host requirements for building HENU OS live-build ISOs.
# ==============================================================================

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "[ERROR] This setup script must be run as root (or with sudo)."
    exit 1
fi

echo "[HENU VM SETUP] Updating APT package repositories..."
apt-get update

echo "[HENU VM SETUP] Installing live-build, debootstrap, xorriso, and packaging tools..."
apt-get install -y --no-install-recommends \
    live-build \
    debootstrap \
    xorriso \
    squashfs-tools \
    mtools \
    dosfstools \
    grub-pc-bin \
    grub-efi-amd64-bin \
    dpkg-dev \
    debhelper \
    python3 \
    python3-yaml \
    python3-pip \
    qemu-system-x86 \
    ovmf \
    git \
    rsync \
    curl \
    wget

echo "[HENU VM SETUP] All build dependencies successfully installed."
