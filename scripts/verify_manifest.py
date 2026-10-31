"""Verifica que cada documento en documents/manifest.json coincida con su
hash SHA-256 registrado. Comando reproducible:

    python scripts/verify_manifest.py

Código de salida 0 si todo coincide, 1 si hay al menos un desajuste.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from provenance.hash_utils import sha256_file  # noqa: E402


def main() -> int:
    manifest_path = REPO_ROOT / "documents" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    ok = True
    for entry in manifest["documentos"]:
        doc_path = REPO_ROOT / entry["path"]
        documento_id = entry["documento_id"]
        expected = entry["sha256"]

        if not doc_path.exists():
            print(f"[FALLO] {documento_id}: archivo no encontrado en {entry['path']}")
            ok = False
            continue

        actual = sha256_file(doc_path)
        if actual != expected:
            print(f"[FALLO] {documento_id}: hash no coincide (esperado={expected}, actual={actual})")
            ok = False
        else:
            print(f"[OK] {documento_id}: hash verificado")

    if ok:
        print("\nTodos los documentos coinciden con su hash registrado.")
        return 0
    print("\nSe encontraron desajustes de hash. Revise documents/manifest.json.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
