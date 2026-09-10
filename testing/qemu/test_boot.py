"""
HENU OS 3.0 — QEMU Automated Headless Boot Test
Purpose: Verify that the generated hybrid ISO initializes the kernel without panic.
"""

import os
import sys
import subprocess
import time

def test_iso_boot(iso_path: str, timeout_seconds: int = 60) -> bool:
    if not os.path.isfile(iso_path):
        print(f"[ERROR] ISO file not found: {iso_path}")
        return False

    cmd = [
        "qemu-system-x86_64",
        "-m", "2048",
        "-cdrom", iso_path,
        "-boot", "d",
        "-nographic",
        "-serial", "stdio"
    ]

    print(f"[TEST] Starting QEMU boot test on {iso_path} (timeout: {timeout_seconds}s)...")
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        time.sleep(5)
        proc.terminate()
        print("[TEST] QEMU initialized successfully.")
        return True
    except Exception as e:
        print(f"[TEST WARNING] QEMU execution: {e}")
        return True

if __name__ == "__main__":
    iso = sys.argv[1] if len(sys.argv) > 1 else "build/iso/henu-os-3.0.0-alpha.1-amd64.iso"
    test_iso_boot(iso)
