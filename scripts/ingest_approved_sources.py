"""Simula el paso de ingesta: solo permite avanzar fuentes cuyos derechos
estén explícitamente verificados en un manifiesto de derechos (ver
rights/rights_manifest_example.json y schemas/rights.schema.json).

Comando reproducible:
    python scripts/ingest_approved_sources.py [ruta_manifiesto_derechos ...]

Sin argumentos, evalúa sources/fuentes_aprobadas.json contra la política
de derechos y reporta qué fuentes quedarían BLOQUEADAS para ingesta real
en el estado actual (se espera que TODAS queden bloqueadas hasta que un
responsable humano verifique cada una).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rights.verifier import evaluate_rights_manifest  # noqa: E402

RIGHTS_DIR = REPO_ROOT / "rights"


def _rights_manifest_for_source(source: dict) -> dict:
    """Prefiere un manifiesto de derechos dedicado en rights/ si existe
    (rights/rights_manifest_<source_id>.json); ese archivo es la fuente de
    verdad porque un responsable humano lo completa explícitamente. Si no
    existe, se deriva un manifiesto conservador desde el registro: nunca
    infiere 'verificado' a partir de texto libre en sources/fuentes_aprobadas.json,
    solo de campos explícitos.
    """
    dedicated_path = RIGHTS_DIR / f"rights_manifest_{source['id']}.json"
    if dedicated_path.exists():
        return json.loads(dedicated_path.read_text(encoding="utf-8"))

    return {
        "source_id": source["id"],
        "permiso_entrenamiento": source.get("permiso_entrenamiento", "NO_VERIFICADO"),
        "permiso_uso_comercial": source.get("permiso_uso_comercial", "NO_VERIFICADO"),
        "permiso_derivados": source.get("permiso_derivados", "NO_VERIFICADO"),
        "evidencia_legal": source.get("evidencia_legal", "NO_VERIFICADO"),
        "estado_verificacion": "NO_VERIFICADO",
    }


def main() -> int:
    registry_path = REPO_ROOT / "sources" / "fuentes_aprobadas.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    bloqueadas = 0
    aprobadas = 0
    for source in registry["fuentes"]:
        manifest = _rights_manifest_for_source(source)
        verdict = evaluate_rights_manifest(manifest)
        if verdict.approved:
            aprobadas += 1
            print(f"[APROBADA] {source['id']} ({source['nombre']}) — lista para ingesta.")
        else:
            bloqueadas += 1
            print(f"[BLOQUEADA] {source['id']} ({source['nombre']}):")
            for reason in verdict.reasons:
                print(f"    - {reason}")

    print(f"\nResumen: {aprobadas} fuente(s) aprobada(s), {bloqueadas} fuente(s) bloqueada(s).")
    if bloqueadas > 0:
        print(
            "Ninguna fuente bloqueada puede ingresar texto a documents/. "
            "Complete rights/ con evidencia real antes de reintentar."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
