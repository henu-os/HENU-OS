"""
HENU OS 3.0 — Build Engine
File: src/utils/hash_utils.py
Purpose: Stateless cryptographic hashing utilities.
         Used by ConfigurationManager (config fingerprinting),
         release_manager (ISO checksum generation), and verifier.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Dict


def md5_file(path: str) -> str:
    """
    Compute the MD5 hex digest of a file's contents.

    Args:
        path — Absolute or relative path to the file.

    Returns:
        Lowercase hex string MD5 hash.

    Raises:
        FileNotFoundError — If the file does not exist.
    """
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_file(path: str) -> str:
    """
    Compute the SHA-256 hex digest of a file's contents.

    Args:
        path — Absolute or relative path to the file.

    Returns:
        Lowercase hex string SHA-256 hash.

    Raises:
        FileNotFoundError — If the file does not exist.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_dict(data: dict) -> str:
    """
    Compute a stable MD5 fingerprint of a dictionary.
    Keys are sorted to ensure deterministic hashing regardless of insertion order.

    Args:
        data — Any JSON-serialisable dictionary.

    Returns:
        Lowercase hex string MD5 hash.
    """
    serialised = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.md5(serialised.encode("utf-8")).hexdigest()


def write_checksum_file(iso_path: str, output_dir: str) -> Dict[str, str]:
    """
    Compute SHA-256 and MD5 checksums for an ISO file and write them
    to standard .sha256 and .md5 sidecar files.

    Args:
        iso_path   — Absolute path to the ISO file.
        output_dir — Directory to write checksum files into.

    Returns:
        Dict with keys 'sha256' and 'md5' containing the hex digests.

    Raises:
        FileNotFoundError — If iso_path does not exist.
    """
    if not os.path.isfile(iso_path):
        raise FileNotFoundError(f"ISO not found at: {iso_path}")

    basename = os.path.basename(iso_path)
    checksums = {
        "sha256": sha256_file(iso_path),
        "md5":    md5_file(iso_path),
    }

    sha256_out = os.path.join(output_dir, f"{basename}.sha256")
    md5_out    = os.path.join(output_dir, f"{basename}.md5")

    with open(sha256_out, "w", encoding="utf-8") as f:
        f.write(f"{checksums['sha256']}  {basename}\n")

    with open(md5_out, "w", encoding="utf-8") as f:
        f.write(f"{checksums['md5']}  {basename}\n")

    return checksums
