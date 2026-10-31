import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from agent.orchestrator import Orchestrator
from provenance.audit_log import AuditLog
from security.policy import is_personalized_advice_request


class TestPersonalizedAdviceDetection(unittest.TestCase):
    def test_detects_first_person_case_language(self):
        casos = [
            "Que debo hacer con mi obra respecto a la recepcion",
            "Represénteme ante la DOM por favor",
            "Mi contrato con el constructor tiene un problema, que hago",
            "Me pueden multar a mí por esto",
        ]
        for pregunta in casos:
            with self.subTest(pregunta=pregunta):
                self.assertTrue(is_personalized_advice_request(pregunta))

    def test_general_informational_question_is_not_personalized(self):
        self.assertFalse(is_personalized_advice_request("Que exige en general la normativa sobre accesibilidad universal"))


class TestOrchestratorEscalatesPersonalizedAdvice(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.audit_log = AuditLog(path=Path(self.tmpdir.name) / "audit_log.jsonl")
        self.orchestrator = Orchestrator(audit_log=self.audit_log)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_personalized_question_forces_escalation_even_with_sources(self):
        response = self.orchestrator.answer("Que debo hacer con mi obra respecto a la recepcion parcial simulada")
        self.assertFalse(response.no_verificado)
        self.assertTrue(response.escalamiento_requerido)
        self.assertIn("consultar", response.recomendacion.lower())


if __name__ == "__main__":
    unittest.main()
