"""Reporta el avance de la cobertura objetivo del dominio (ver
sources/cobertura_objetivo.json), reutilizando la misma política de
derechos que scripts/ingest_approved_sources.py.

Comando reproducible:
    python scripts/coverage_report.py

No aprueba ni rechaza nada por sí mismo: solo resume el estado ya
registrado en sources/cobertura_objetivo.json y valida que ningún
objetivo esté marcado 'aprobada' sin un manifiesto de derechos real y
efectivamente aprobado en rights/.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rights.verifier import evaluate_rights_manifest  # noqa: E402

COBERTURA_PATH = REPO_ROOT / "sources" / "cobertura_objetivo.json"


def _load_rights_manifest(ref: str) -> dict | None:
    if not ref:
        return None
    path = REPO_ROOT / ref
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    cobertura = json.loads(COBERTURA_PATH.read_text(encoding="utf-8"))
    objetivos = cobertura["objetivos"]

    estados = Counter(o["estado"] for o in objetivos)
    bloques = Counter(o["bloque_tematico"] for o in objetivos)

    print(f"Cobertura objetivo: {len(objetivos)} normas/áreas registradas.\n")

    print("Por estado:")
    for estado in ("pendiente_investigacion", "investigada_no_verificada", "rechazada", "aprobada"):
        print(f"  {estado}: {estados.get(estado, 0)}")

    print("\nPor bloque temático:")
    for bloque, cantidad in sorted(bloques.items()):
        print(f"  {bloque}: {cantidad}")

    inconsistencias = []
    for objetivo in objetivos:
        if objetivo["estado"] != "aprobada":
            continue
        manifest = _load_rights_manifest(objetivo.get("rights_manifest_ref"))
        if manifest is None:
            inconsistencias.append(
                f"{objetivo['id']}: estado 'aprobada' sin rights_manifest_ref válido"
            )
            continue
        verdict = evaluate_rights_manifest(manifest)
        if not verdict.approved:
            inconsistencias.append(
                f"{objetivo['id']}: estado 'aprobada' pero el manifiesto real en "
                f"'{objetivo['rights_manifest_ref']}' NO está aprobado ({', '.join(verdict.reasons)})"
            )

    print()
    if inconsistencias:
        print("INCONSISTENCIAS DETECTADAS (estado 'aprobada' sin respaldo real):")
        for msg in inconsistencias:
            print(f"  - {msg}")
        return 1

    print("Sin inconsistencias: ningún objetivo está marcado 'aprobada' sin respaldo real en rights/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
