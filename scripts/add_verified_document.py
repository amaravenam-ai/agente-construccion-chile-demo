"""Herramienta de ingesta real: añade un documento ya preparado a
documents/manifest.json, pero SOLO si su fuente tiene un manifiesto de
derechos real y aprobado en rights/ (los tres permisos en 'si' y
estado_verificacion='verificado'). El gate de derechos está embebido acá,
no en un paso separado que se puede olvidar correr.

Comando reproducible (desde la raíz del repositorio):
    python scripts/add_verified_document.py <ruta_al_documento.json>

El documento de entrada debe:
  - Ya estar ubicado en su ruta final dentro del repositorio (p. ej. bajo
    documents/synthetic/ o una futura documents/real/), porque el 'path'
    registrado en el manifiesto es relativo a esa ubicación.
  - Ser un JSON con, como mínimo, los campos requeridos por
    schemas/document_manifest.schema.json: documento_id, norma_id,
    source_id, tipo_norma, materia, organismo, fecha, estado_vigencia,
    version, es_sintetico, articulos.

Usar --dry-run para ver qué se agregaría sin escribir nada.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from provenance.hash_utils import sha256_file  # noqa: E402
from rights.verifier import evaluate_rights_manifest  # noqa: E402

REQUIRED_DOCUMENT_FIELDS = [
    "documento_id", "norma_id", "source_id", "tipo_norma", "materia",
    "organismo", "fecha", "estado_vigencia", "version", "es_sintetico",
    "articulos",
]


@dataclass
class AddDocumentResult:
    ok: bool
    message: str
    entry: Optional[dict] = None


def _load_rights_manifest(source_id: str, rights_dir: Path) -> Optional[dict]:
    path = rights_dir / f"rights_manifest_{source_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def add_document(
    document_path: Path,
    manifest_path: Path,
    rights_dir: Path,
    repo_root: Path,
    dry_run: bool = False,
) -> AddDocumentResult:
    document_path = Path(document_path)
    if not document_path.exists():
        return AddDocumentResult(ok=False, message=f"No existe el archivo: {document_path}")

    document = json.loads(document_path.read_text(encoding="utf-8"))

    faltantes = [f for f in REQUIRED_DOCUMENT_FIELDS if f not in document]
    if faltantes:
        return AddDocumentResult(
            ok=False,
            message=f"El documento no tiene los campos requeridos: {', '.join(faltantes)}",
        )

    source_id = document["source_id"]
    manifest = _load_rights_manifest(source_id, rights_dir)
    if manifest is None:
        return AddDocumentResult(
            ok=False,
            message=(
                f"No existe rights/rights_manifest_{source_id}.json -- "
                "no se puede verificar derechos, ingesta rechazada."
            ),
        )

    verdict = evaluate_rights_manifest(manifest)
    if not verdict.approved:
        return AddDocumentResult(
            ok=False,
            message=(
                f"Fuente '{source_id}' no aprobada para ingesta: {', '.join(verdict.reasons)}"
            ),
        )

    doc_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing_ids = {d["documento_id"] for d in doc_manifest["documentos"]}
    if document["documento_id"] in existing_ids:
        return AddDocumentResult(
            ok=False,
            message=f"documento_id '{document['documento_id']}' ya existe en {manifest_path}",
        )

    relative_path = document_path.resolve().relative_to(repo_root.resolve()).as_posix()
    entry = {
        "documento_id": document["documento_id"],
        "norma_id": document["norma_id"],
        "source_id": source_id,
        "tipo_norma": document["tipo_norma"],
        "materia": document["materia"],
        "organismo": document["organismo"],
        "fecha": document["fecha"],
        "estado_vigencia": document["estado_vigencia"],
        "version": document["version"],
        "sha256": sha256_file(document_path),
        "path": relative_path,
        "es_sintetico": document["es_sintetico"],
    }
    if "region" in document:
        entry["region"] = document["region"]
    if "comuna" in document:
        entry["comuna"] = document["comuna"]

    if dry_run:
        return AddDocumentResult(
            ok=True,
            message=f"[dry-run] Se agregaría '{entry['documento_id']}' (fuente '{source_id}', aprobada).",
            entry=entry,
        )

    doc_manifest["documentos"].append(entry)
    manifest_path.write_text(
        json.dumps(doc_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return AddDocumentResult(
        ok=True,
        message=f"Agregado '{entry['documento_id']}' (fuente '{source_id}', aprobada) a {manifest_path}.",
        entry=entry,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("documento", type=str, help="Ruta al JSON del documento ya preparado.")
    parser.add_argument("--manifest", type=str, default=str(REPO_ROOT / "documents" / "manifest.json"))
    parser.add_argument("--rights-dir", type=str, default=str(REPO_ROOT / "rights"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    result = add_document(
        document_path=Path(args.documento),
        manifest_path=Path(args.manifest),
        rights_dir=Path(args.rights_dir),
        repo_root=REPO_ROOT,
        dry_run=args.dry_run,
    )

    print(result.message)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
