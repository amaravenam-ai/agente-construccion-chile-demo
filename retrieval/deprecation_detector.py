"""Detección de documentos derogados o con vigencia ambigua.

Ningún documento marcado 'derogada', 'proyecto' o 'no_verificada' debe
usarse como fundamento de una respuesta sin advertencia explícita.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from retrieval.index import Document

AMBIGUOUS_STATES = {"no_verificada", "proyecto"}


@dataclass
class VigenciaAlerta:
    documento_id: str
    estado_vigencia: str
    tipo_alerta: str  # "derogada" | "ambigua" | "ninguna"
    mensaje: str


def check_vigencia(doc: Document) -> VigenciaAlerta:
    if doc.estado_vigencia == "derogada":
        return VigenciaAlerta(
            documento_id=doc.documento_id,
            estado_vigencia=doc.estado_vigencia,
            tipo_alerta="derogada",
            mensaje="Este documento está derogado y no debe citarse como norma vigente.",
        )
    if doc.estado_vigencia in AMBIGUOUS_STATES:
        return VigenciaAlerta(
            documento_id=doc.documento_id,
            estado_vigencia=doc.estado_vigencia,
            tipo_alerta="ambigua",
            mensaje=(
                f"Vigencia ambigua o no confirmada (estado='{doc.estado_vigencia}'); "
                "requiere verificación antes de usarse como fundamento."
            ),
        )
    return VigenciaAlerta(
        documento_id=doc.documento_id,
        estado_vigencia=doc.estado_vigencia,
        tipo_alerta="ninguna",
        mensaje="Sin alertas de vigencia conocidas.",
    )


def filter_usable_documents(documents: List[Document]) -> List[Document]:
    return [d for d in documents if check_vigencia(d).tipo_alerta == "ninguna"]
