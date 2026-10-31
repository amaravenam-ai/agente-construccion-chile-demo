"""Genera un resumen de auditoría en tiempo de ejecución: estructura de
carpetas, verificación de hashes, estado de derechos de fuentes y
resultado del harness de evaluación.

Comando reproducible:
    python scripts/run_audit.py

Este script NO reemplaza docs/INFORME_AUDITORIA_INICIAL.md (que es el
informe entregado con esta fase); lo complementa mostrando el estado
actual re-computado.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REQUIRED_DIRS = [
    "app", "agent", "retrieval", "documents", "sources", "rights",
    "provenance", "evaluation", "security", "schemas", "tests", "docs", "scripts",
]


def check_structure() -> bool:
    print("== Estructura de carpetas ==")
    ok = True
    for d in REQUIRED_DIRS:
        path = REPO_ROOT / d
        exists = path.is_dir()
        print(f"[{'OK' if exists else 'FALTA'}] {d}/")
        ok = ok and exists
    return ok


def run_subscript(relative_path: str) -> int:
    print(f"\n== Ejecutando {relative_path} ==")
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / relative_path)],
        cwd=str(REPO_ROOT),
    )
    return result.returncode


def main() -> int:
    structure_ok = check_structure()

    manifest_code = run_subscript("scripts/verify_manifest.py")
    ingest_code = run_subscript("scripts/ingest_approved_sources.py")
    coverage_code = run_subscript("scripts/coverage_report.py")
    eval_code = run_subscript("evaluation/run_eval.py")

    print("\n== Resumen de auditoría ==")
    print(f"Estructura de carpetas completa: {structure_ok}")
    print(f"Verificación de hashes: {'OK' if manifest_code == 0 else 'FALLÓ'}")
    print(f"Ingesta de fuentes (se espera 0 fuentes aprobadas en esta fase): código {ingest_code}")
    print(f"Cobertura objetivo del dominio: {'OK (sin inconsistencias)' if coverage_code == 0 else 'FALLÓ'}")
    print(f"Harness de evaluación: {'OK' if eval_code == 0 else 'FALLÓ'}")
    print(
        "\nRecordatorio: ninguna fuente jurídica real ha sido verificada todavía. "
        "El agente opera solo con fixtures sintéticos (documents/synthetic/). "
        "Ver docs/BLOQUEADORES.md para la lista de bloqueadores antes de producción."
    )

    return 0 if structure_ok and all(code == 0 for code in (manifest_code, ingest_code, coverage_code, eval_code)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
