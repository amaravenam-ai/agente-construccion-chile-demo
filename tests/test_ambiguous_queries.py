import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from agent.orchestrator import Orchestrator
from provenance.audit_log import AuditLog


class TestAmbiguousQueries(unittest.TestCase):
    """Una consulta genérica que calza con documentos de distinto tipo y
    valor normativo debe advertir la ambigüedad en vez de presentar una
    única respuesta como si fuera inequívoca."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.audit_log = AuditLog(path=Path(self.tmpdir.name) / "audit_log.jsonl")
        self.orchestrator = Orchestrator(audit_log=self.audit_log)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_generic_query_matching_mixed_source_types_flags_risk(self):
        response = self.orchestrator.answer("obras")
        self.assertFalse(response.no_verificado)
        tipos_mencionados = [r for r in response.riesgos_informacion_faltante if "distintos tipos de fuente" in r]
        self.assertTrue(tipos_mencionados, f"riesgos obtenidos: {response.riesgos_informacion_faltante}")

    def test_ambiguous_query_lowers_confidence_when_escalation_required(self):
        # Al combinar una pregunta ambigua con lenguaje de asesoría
        # personalizada, el nivel de confianza no debe ser 'alto'.
        response = self.orchestrator.answer("Que debo hacer yo respecto a mi obra")
        self.assertNotEqual(response.nivel_confianza, "alto")


if __name__ == "__main__":
    unittest.main()
