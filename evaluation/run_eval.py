"""Harness de evaluación reproducible.

Comando reproducible (desde la raíz del repositorio):
    python evaluation/run_eval.py

Carga cada caso en evaluation/eval_cases/*.json, ejecuta el orquestador
y verifica las expectativas declaradas en el propio caso. Código de
salida 0 si todos los casos pasan, 1 si alguno falla.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent.orchestrator import Orchestrator  # noqa: E402
from evaluation.metrics import CaseResult, summarize  # noqa: E402
from provenance.audit_log import AuditLog  # noqa: E402
from retrieval.search import SearchFilters  # noqa: E402

EVAL_CASES_DIR = REPO_ROOT / "evaluation" / "eval_cases"
EVAL_AUDIT_LOG_PATH = REPO_ROOT / "evaluation" / "results" / "eval_audit_log.jsonl"


def _load_cases() -> List[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(EVAL_CASES_DIR.glob("*.json"))
    ]


def _run_case(orchestrator: Orchestrator, case: dict) -> CaseResult:
    filtros_raw = case.get("filtros", {}) or {}
    filters = SearchFilters(**filtros_raw)
    response = orchestrator.answer(case["pregunta"], filters=filters)
    expectativas = case.get("expectativas", {})
    details: List[str] = []
    passed = True

    if "no_verificado" in expectativas:
        esperado = expectativas["no_verificado"]
        if response.no_verificado != esperado:
            passed = False
            details.append(f"no_verificado esperado={esperado}, obtenido={response.no_verificado}")

    if "escalamiento_requerido" in expectativas:
        esperado = expectativas["escalamiento_requerido"]
        if response.escalamiento_requerido != esperado:
            passed = False
            details.append(
                f"escalamiento_requerido esperado={esperado}, obtenido={response.escalamiento_requerido}"
            )

    if "documentos_esperados_incluyen" in expectativas:
        for doc_id in expectativas["documentos_esperados_incluyen"]:
            if doc_id not in response.documentos_utilizados:
                passed = False
                details.append(f"se esperaba que la respuesta usara el documento '{doc_id}' y no aparece")

    if "documentos_prohibidos" in expectativas:
        for doc_id in expectativas["documentos_prohibidos"]:
            if doc_id in response.documentos_utilizados:
                passed = False
                details.append(f"el documento prohibido '{doc_id}' aparece en la respuesta")

    if "riesgo_menciona" in expectativas:
        texto_riesgos = " ".join(response.riesgos_informacion_faltante)
        if expectativas["riesgo_menciona"] not in texto_riesgos:
            passed = False
            details.append(
                f"se esperaba que los riesgos mencionaran '{expectativas['riesgo_menciona']}'; "
                f"riesgos obtenidos: {texto_riesgos!r}"
            )

    return CaseResult(case_id=case["id"], passed=passed, details=details)


def main() -> int:
    cases = _load_cases()
    audit_log = AuditLog(path=EVAL_AUDIT_LOG_PATH)
    orchestrator = Orchestrator(audit_log=audit_log)

    results = [_run_case(orchestrator, case) for case in cases]
    print(summarize(results))

    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
