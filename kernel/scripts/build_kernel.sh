#!/usr/bin/env bash
# ==============================================================================
# HENU OS 3.0 Custom Kernel Compilation Script
# Base: Debian GNU/Linux 13 (Trixie)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="${KERNEL_ROOT}/../build/deb"

echo "[HENU KERNEL] Initializing Debian kernel build workspace..."
echo "[HENU KERNEL] Strategy: Initial builds use official Debian 'linux-image-amd64'."
echo "[HENU KERNEL] Custom compilation available for future performance tuning."

mkdir -p "${OUTPUT_DIR}"
echo "[HENU KERNEL] Ready."
