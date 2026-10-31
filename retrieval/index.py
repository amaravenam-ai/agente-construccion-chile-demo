"""Carga el índice documental desde documents/manifest.json.

No hay dependencia de ningún motor de búsqueda externo: el índice es
una lista en memoria de dataclasses, suficiente para el volumen de
fixtures sintéticos de esta fase y fácil de auditar.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "documents" / "manifest.json"


@dataclass
class Articulo:
    numero: str
    texto: str
    pagina: Optional[str] = None


@dataclass
class Document:
    documento_id: str
    norma_id: str
    source_id: str
    tipo_norma: str
    materia: str
    organismo: str
    fecha: str
    estado_vigencia: str
    version: str
    sha256: str
    path: str
    es_sintetico: bool
    region: Optional[str] = None
    comuna: Optional[str] = None
    articulos: List[Articulo] = field(default_factory=list)
    titulo: Optional[str] = None
    vinculante: Optional[bool] = None


def _load_articulos(raw_articulos: list) -> List[Articulo]:
    return [
        Articulo(numero=a["numero"], texto=a["texto"], pagina=a.get("pagina"))
        for a in raw_articulos
    ]


def load_index(manifest_path: Path = MANIFEST_PATH, repo_root: Path = REPO_ROOT) -> List[Document]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    documents: List[Document] = []
    for entry in manifest["documentos"]:
        doc_path = Path(repo_root) / entry["path"]
        raw = json.loads(doc_path.read_text(encoding="utf-8"))
        documents.append(
            Document(
                documento_id=entry["documento_id"],
                norma_id=entry["norma_id"],
                source_id=entry["source_id"],
                tipo_norma=entry["tipo_norma"],
                materia=entry["materia"],
                organismo=entry["organismo"],
                fecha=entry["fecha"],
                estado_vigencia=entry["estado_vigencia"],
                version=entry["version"],
                sha256=entry["sha256"],
                path=entry["path"],
                es_sintetico=entry["es_sintetico"],
                region=entry.get("region"),
                comuna=entry.get("comuna"),
                articulos=_load_articulos(raw.get("articulos", [])),
                titulo=raw.get("titulo"),
                vinculante=raw.get("vinculante"),
            )
        )
    return documents
