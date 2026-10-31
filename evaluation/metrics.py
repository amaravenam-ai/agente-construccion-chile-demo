"""Métricas simples de agregación para el harness de evaluación."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    details: List[str]


def summarize(results: List[CaseResult]) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    lines = [f"Casos evaluados: {total}", f"Casos aprobados: {passed}", f"Casos fallidos: {total - passed}"]
    for r in results:
        estado = "OK" if r.passed else "FALLO"
        lines.append(f"  [{estado}] {r.case_id}")
        for d in r.details:
            lines.append(f"      - {d}")
    return "\n".join(lines)
