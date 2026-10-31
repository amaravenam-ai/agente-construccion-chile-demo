"""Construcción de citas exactas a partir de resultados de búsqueda.

Las citas se generan de forma determinista desde los metadatos del
documento, nunca desde texto generado por el LLM, para evitar citas
inventadas.
"""
from __future__ import annotations

from retrieval.search import SearchHit


def build_citation(hit: SearchHit) -> str:
    doc = hit.document
    art = hit.articulo
    pagina = f", pág. {art.pagina}" if art.pagina else ""
    etiqueta_sintetico = " [FIXTURE SINTÉTICO DE PRUEBA]" if doc.es_sintetico else ""
    return (
        f"{doc.titulo or doc.documento_id} — {art.numero}{pagina} "
        f"(versión {doc.version}, estado: {doc.estado_vigencia}){etiqueta_sintetico}"
    )


def build_norma_label(hit: SearchHit) -> str:
    doc = hit.document
    etiqueta_sintetico = " [FIXTURE SINTÉTICO DE PRUEBA]" if doc.es_sintetico else ""
    return f"{doc.titulo or doc.documento_id} [{doc.tipo_norma}] ({doc.organismo}){etiqueta_sintetico}"
