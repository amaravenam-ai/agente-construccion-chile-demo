import unittest

import tests._pathfix  # noqa: F401
from rights.verifier import evaluate_rights_manifest


class TestRightsVerifier(unittest.TestCase):
    def test_unverified_manifest_is_rejected(self):
        manifest = {
            "source_id": "src-test",
            "permiso_entrenamiento": "NO_VERIFICADO",
            "permiso_uso_comercial": "NO_VERIFICADO",
            "permiso_derivados": "NO_VERIFICADO",
            "evidencia_legal": "NO_VERIFICADO",
            "estado_verificacion": "NO_VERIFICADO",
        }
        verdict = evaluate_rights_manifest(manifest)
        self.assertFalse(verdict.approved)
        self.assertTrue(len(verdict.reasons) > 0)

    def test_partially_verified_manifest_is_rejected(self):
        manifest = {
            "source_id": "src-test",
            "permiso_entrenamiento": "si",
            "permiso_uso_comercial": "no",
            "permiso_derivados": "si",
            "evidencia_legal": "enlace archivado a los términos de uso",
            "estado_verificacion": "verificado",
        }
        verdict = evaluate_rights_manifest(manifest)
        self.assertFalse(verdict.approved)

    def test_fully_verified_manifest_is_approved(self):
        manifest = {
            "source_id": "src-test",
            "permiso_entrenamiento": "si",
            "permiso_uso_comercial": "si",
            "permiso_derivados": "si",
            "evidencia_legal": "enlace archivado a los términos de uso",
            "estado_verificacion": "verificado",
        }
        verdict = evaluate_rights_manifest(manifest)
        self.assertTrue(verdict.approved)
        self.assertEqual(verdict.reasons, [])

    def test_registered_sources_are_all_unverified_in_current_phase(self):
        import json
        from pathlib import Path

        registry_path = Path(__file__).resolve().parent.parent / "sources" / "fuentes_aprobadas.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        for source in registry["fuentes"]:
            manifest = {
                "source_id": source["id"],
                "permiso_entrenamiento": source.get("permiso_entrenamiento"),
                "permiso_uso_comercial": source.get("permiso_uso_comercial"),
                "permiso_derivados": source.get("permiso_derivados"),
                "evidencia_legal": source.get("evidencia_legal"),
                "estado_verificacion": "NO_VERIFICADO",
            }
            verdict = evaluate_rights_manifest(manifest)
            self.assertFalse(
                verdict.approved,
                f"La fuente '{source['id']}' no debería estar aprobada en esta fase inicial.",
            )


if __name__ == "__main__":
    unittest.main()
