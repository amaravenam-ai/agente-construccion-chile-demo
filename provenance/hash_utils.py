"""Utilidades deterministas de hashing para verificar procedencia documental."""
from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def verify_file_hash(path: Path, expected_sha256: str) -> bool:
    if expected_sha256 == "NO_VERIFICADO":
        return False
    return sha256_file(path) == expected_sha256
