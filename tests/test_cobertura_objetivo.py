import json
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from rights.verifier import evaluate_rights_manifest

REPO_ROOT = Path(__file__).resolve().parent.parent
COBERTURA_PATH = REPO_ROOT / "sources" / "cobertura_objetivo.json"

REQUIRED_FIELDS = {
    "id", "nombre", "institucion_referente", "materia",
    "tipo_norma", "bloque_tematico", "estado",
}
VALID_ESTADOS = {"pendiente_investigacion", "investigada_no_verificada", "rechazada", "aprobada"}
VALID_TIPO_NORMA = {"ley", "reglamento", "circular", "dictamen", "jurisprudencia", "opinion", "proyecto_de_ley", "otro"}


class TestCoberturaObjetivo(unittest.TestCase):
    def setUp(self):
        self.cobertura = json.loads(COBERTURA_PATH.read_text(encoding="utf-8"))
        self.objetivos = self.cobertura["objetivos"]

    def test_no_esta_vacio(self):
        self.assertGreater(len(self.objetivos), 0)

    def test_ids_unicos(self):
        ids = [o["id"] for o in self.objetivos]
        self.assertEqual(len(ids), len(set(ids)), "hay id duplicados en cobertura_objetivo.json")

    def test_campos_requeridos_presentes(self):
        for objetivo in self.objetivos:
            faltantes = REQUIRED_FIELDS - set(objetivo.keys())
            self.assertEqual(faltantes, set(), f"{objetivo.get('id')}: faltan campos {faltantes}")

    def test_estado_dentro_de_enum_valido(self):
        for objetivo in self.objetivos:
            self.assertIn(objetivo["estado"], VALID_ESTADOS, f"{objetivo['id']}: estado inválido")

    def test_tipo_norma_dentro_de_enum_valido(self):
        for objetivo in self.objetivos:
            self.assertIn(objetivo["tipo_norma"], VALID_TIPO_NORMA, f"{objetivo['id']}: tipo_norma inválido")

    def test_ningun_objetivo_esta_aprobado_todavia(self):
        # Refleja el estado real del proyecto: cero fuentes verificadas.
        aprobados = [o["id"] for o in self.objetivos if o["estado"] == "aprobada"]
        self.assertEqual(aprobados, [], f"objetivos marcados 'aprobada' sin ingesta real aún: {aprobados}")

    def test_objetivos_rechazados_o_investigados_referencian_manifiesto_existente(self):
        for objetivo in self.objetivos:
            if objetivo["estado"] in ("rechazada", "investigada_no_verificada"):
                ref = objetivo.get("rights_manifest_ref")
                self.assertIsNotNone(ref, f"{objetivo['id']}: falta rights_manifest_ref para estado '{objetivo['estado']}'")
                self.assertTrue((REPO_ROOT / ref).exists(), f"{objetivo['id']}: {ref} no existe")

    def test_ningun_objetivo_aprobado_sin_respaldo_real_en_rights(self):
        """Si en el futuro alguien marca un objetivo como 'aprobada', este test
        debe fallar a menos que el manifiesto de derechos referenciado esté
        realmente aprobado por rights/verifier.py."""
        for objetivo in self.objetivos:
            if objetivo["estado"] != "aprobada":
                continue
            ref = objetivo.get("rights_manifest_ref")
            self.assertIsNotNone(ref, f"{objetivo['id']}: 'aprobada' sin rights_manifest_ref")
            manifest_path = REPO_ROOT / ref
            self.assertTrue(manifest_path.exists(), f"{objetivo['id']}: {ref} no existe")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            verdict = evaluate_rights_manifest(manifest)
            self.assertTrue(
                verdict.approved,
                f"{objetivo['id']}: marcado 'aprobada' pero el manifiesto real no lo respalda: {verdict.reasons}",
            )

    def test_rechazos_de_inn_y_poder_judicial_tienen_evidencia_de_rechazo_real(self):
        rechazados = {o["id"]: o for o in self.objetivos if o["estado"] == "rechazada"}
        for objetivo_id, objetivo in rechazados.items():
            manifest_path = REPO_ROOT / objetivo["rights_manifest_ref"]
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                manifest["estado_verificacion"], "rechazado",
                f"{objetivo_id}: estado 'rechazada' en cobertura pero el manifiesto real no dice 'rechazado'",
            )


if __name__ == "__main__":
    unittest.main()
