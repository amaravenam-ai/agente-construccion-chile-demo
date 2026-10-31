import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from agent.orchestrator import Orchestrator
from agent.response_builder import STANDARD_NO_VERIFICADO_MESSAGE
from provenance.audit_log import AuditLog


class TestNoSourceResponse(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.audit_log = AuditLog(path=Path(self.tmpdir.name) / "audit_log.jsonl")
        self.orchestrator = Orchestrator(audit_log=self.audit_log)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_out_of_domain_question_returns_standard_message(self):
        response = self.orchestrator.answer("Cual es la capital de Francia")
        self.assertTrue(response.no_verificado)
        self.assertEqual(response.resumen, STANDARD_NO_VERIFICADO_MESSAGE)
        self.assertEqual(response.nivel_confianza, "no_verificado")

    def test_response_still_includes_all_required_fields(self):
        response = self.orchestrator.answer("Cual es la capital de Francia")
        data = response.to_dict()
        campos_requeridos = [
            "resumen", "jurisdiccion", "fecha_consulta", "norma_o_documento",
            "articulo_seccion_pagina", "vigencia_conocida", "nivel_confianza",
            "supuestos", "riesgos_informacion_faltante", "advertencia",
            "recomendacion", "no_verificado",
        ]
        for campo in campos_requeridos:
            self.assertIn(campo, data)
        self.assertIn("abogado", data["advertencia"].lower())

    def test_jurisdiccion_always_chile(self):
        response = self.orchestrator.answer("pregunta cualquiera sin fuente disponible")
        self.assertEqual(response.jurisdiccion, "Chile")


if __name__ == "__main__":
    unittest.main()
