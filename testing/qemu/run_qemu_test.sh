#!/usr/bin/env bash
# ==============================================================================
# HENU OS 3.0 Automated QEMU Boot Test Launcher
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ISO_PATH="${1:-"${WORKSPACE_ROOT}/build/iso/henu-os-3.0.0-alpha.1-amd64.iso"}"

if [ ! -f "${ISO_PATH}" ]; then
    echo "[TEST ERROR] ISO not found at: ${ISO_PATH}"
    exit 1
fi

echo "[TEST INFO] Launching QEMU boot test for: ${ISO_PATH}"
qemu-system-x86_64 \
    -enable-kvm \
    -m 4096 \
    -smp 2 \
    -cdrom "${ISO_PATH}" \
    -boot d \
    -vga virtio \
    -display default
