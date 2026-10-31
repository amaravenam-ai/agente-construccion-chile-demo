"""Verificación de derechos de fuentes antes de permitir su ingesta.

Ninguna fuente puede pasar a documents/ sin que los tres permisos
(entrenamiento, uso comercial, derivados) estén explícitamente en "si"
y el estado de verificación sea "verificado". Esto materializa la
restricción de no entrenar/usar contenido cuyos derechos no estén
verificados.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


REQUIRED_PERMISSIONS = ("permiso_entrenamiento", "permiso_uso_comercial", "permiso_derivados")


@dataclass
class RightsVerdict:
    source_id: str
    approved: bool
    reasons: List[str]


def evaluate_rights_manifest(manifest: dict) -> RightsVerdict:
    source_id = manifest.get("source_id", "NO_VERIFICADO")
    reasons: List[str] = []

    if manifest.get("estado_verificacion") != "verificado":
        reasons.append(
            f"estado_verificacion='{manifest.get('estado_verificacion')}' (se requiere 'verificado')"
        )

    for field in REQUIRED_PERMISSIONS:
        value = manifest.get(field)
        if value != "si":
            reasons.append(f"{field}='{value}' (se requiere 'si')")

    if manifest.get("evidencia_legal") in (None, "", "NO_VERIFICADO"):
        reasons.append("evidencia_legal ausente o NO_VERIFICADO")

    return RightsVerdict(source_id=source_id, approved=(len(reasons) == 0), reasons=reasons)
