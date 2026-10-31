"""Comparación determinista entre versiones de una misma norma."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from retrieval.index import Document


@dataclass
class ArticleDiff:
    numero: str
    texto_v1: Optional[str]
    texto_v2: Optional[str]
    cambio: str  # "agregado" | "eliminado" | "modificado" | "sin_cambios"


@dataclass
class VersionComparison:
    norma_id: str
    version_1: str
    version_2: str
    diffs: List[ArticleDiff]


def compare_versions(doc_v1: Document, doc_v2: Document) -> VersionComparison:
    if doc_v1.norma_id != doc_v2.norma_id:
        raise ValueError(
            f"Los documentos '{doc_v1.documento_id}' y '{doc_v2.documento_id}' "
            "no comparten norma_id; no son versiones comparables."
        )
    articulos_v1 = {a.numero: a.texto for a in doc_v1.articulos}
    articulos_v2 = {a.numero: a.texto for a in doc_v2.articulos}
    numeros = sorted(set(articulos_v1) | set(articulos_v2))

    diffs: List[ArticleDiff] = []
    for numero in numeros:
        t1 = articulos_v1.get(numero)
        t2 = articulos_v2.get(numero)
        if t1 is None:
            cambio = "agregado"
        elif t2 is None:
            cambio = "eliminado"
        elif t1 != t2:
            cambio = "modificado"
        else:
            cambio = "sin_cambios"
        diffs.append(ArticleDiff(numero=numero, texto_v1=t1, texto_v2=t2, cambio=cambio))

    return VersionComparison(
        norma_id=doc_v1.norma_id,
        version_1=doc_v1.version,
        version_2=doc_v2.version,
        diffs=diffs,
    )


def find_versions(documents: List[Document], norma_id: str) -> List[Document]:
    return sorted((d for d in documents if d.norma_id == norma_id), key=lambda d: d.version)
