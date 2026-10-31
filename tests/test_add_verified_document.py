import json
import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from scripts.add_verified_document import add_document

REJECTED_SOURCE_ID = "src-test-no-aprobado"
APPROVED_SOURCE_ID = "src-test-aprobado"


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _sample_document(source_id: str, documento_id: str) -> dict:
    return {
        "documento_id": documento_id,
        "norma_id": f"norma-{documento_id}",
        "source_id": source_id,
        "tipo_norma": "ley",
        "materia": "prueba de ingesta",
        "organismo": "Organismo de Prueba",
        "fecha": "2024-01-01",
        "estado_vigencia": "vigente",
        "version": "1.0",
        "es_sintetico": True,
        "titulo": "Documento de prueba para add_verified_document",
        "articulos": [{"numero": "Artículo 1", "texto": "Texto de prueba.", "pagina": "1"}],
    }


class TestAddVerifiedDocument(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.tmpdir.name)
        self.rights_dir = self.repo_root / "rights"
        self.documents_dir = self.repo_root / "documents" / "synthetic"
        self.manifest_path = self.repo_root / "documents" / "manifest.json"

        _write_json(self.manifest_path, {"documentos": []})

        _write_json(
            self.rights_dir / f"rights_manifest_{REJECTED_SOURCE_ID}.json",
            {
                "source_id": REJECTED_SOURCE_ID,
                "permiso_entrenamiento": "NO_VERIFICADO",
                "permiso_uso_comercial": "NO_VERIFICADO",
                "permiso_derivados": "NO_VERIFICADO",
                "evidencia_legal": "NO_VERIFICADO",
                "estado_verificacion": "NO_VERIFICADO",
            },
        )
        _write_json(
            self.rights_dir / f"rights_manifest_{APPROVED_SOURCE_ID}.json",
            {
                "source_id": APPROVED_SOURCE_ID,
                "permiso_entrenamiento": "si",
                "permiso_uso_comercial": "si",
                "permiso_derivados": "si",
                "evidencia_legal": "Licencia de prueba ficticia, solo para test.",
                "estado_verificacion": "verificado",
            },
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_rechaza_fuente_sin_derechos_verificados(self):
        doc_path = self.documents_dir / "doc-rechazado.json"
        _write_json(doc_path, _sample_document(REJECTED_SOURCE_ID, "doc-rechazado"))

        result = add_document(doc_path, self.manifest_path, self.rights_dir, self.repo_root)

        self.assertFalse(result.ok)
        self.assertIn("no aprobada", result.message)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["documentos"], [])

    def test_rechaza_fuente_sin_manifiesto_de_derechos(self):
        doc_path = self.documents_dir / "doc-sin-manifiesto.json"
        _write_json(doc_path, _sample_document("src-inexistente", "doc-sin-manifiesto"))

        result = add_document(doc_path, self.manifest_path, self.rights_dir, self.repo_root)

        self.assertFalse(result.ok)
        self.assertIn("No existe rights/", result.message)

    def test_acepta_fuente_con_derechos_verificados(self):
        doc_path = self.documents_dir / "doc-aprobado.json"
        _write_json(doc_path, _sample_document(APPROVED_SOURCE_ID, "doc-aprobado"))

        result = add_document(doc_path, self.manifest_path, self.rights_dir, self.repo_root)

        self.assertTrue(result.ok, result.message)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        ids = [d["documento_id"] for d in manifest["documentos"]]
        self.assertIn("doc-aprobado", ids)
        entry = next(d for d in manifest["documentos"] if d["documento_id"] == "doc-aprobado")
        self.assertEqual(entry["source_id"], APPROVED_SOURCE_ID)
        self.assertEqual(len(entry["sha256"]), 64)
        self.assertEqual(entry["path"], "documents/synthetic/doc-aprobado.json")

    def test_dry_run_no_escribe_nada(self):
        doc_path = self.documents_dir / "doc-dry-run.json"
        _write_json(doc_path, _sample_document(APPROVED_SOURCE_ID, "doc-dry-run"))

        result = add_document(doc_path, self.manifest_path, self.rights_dir, self.repo_root, dry_run=True)

        self.assertTrue(result.ok)
        self.assertIn("dry-run", result.message)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["documentos"], [])

    def test_rechaza_documento_id_duplicado(self):
        doc_path = self.documents_dir / "doc-aprobado.json"
        _write_json(doc_path, _sample_document(APPROVED_SOURCE_ID, "doc-aprobado"))
        first = add_document(doc_path, self.manifest_path, self.rights_dir, self.repo_root)
        self.assertTrue(first.ok)

        second = add_document(doc_path, self.manifest_path, self.rights_dir, self.repo_root)
        self.assertFalse(second.ok)
        self.assertIn("ya existe", second.message)

    def test_rechaza_documento_con_campos_faltantes(self):
        doc_path = self.documents_dir / "doc-incompleto.json"
        _write_json(doc_path, {"documento_id": "doc-incompleto"})

        result = add_document(doc_path, self.manifest_path, self.rights_dir, self.repo_root)

        self.assertFalse(result.ok)
        self.assertIn("campos requeridos", result.message)


if __name__ == "__main__":
    unittest.main()
