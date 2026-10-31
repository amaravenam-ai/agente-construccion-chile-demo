import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from agent.orchestrator import Orchestrator
from agent.response_builder import STANDARD_NO_VERIFICADO_MESSAGE
from provenance.audit_log import AuditLog


class TestRejectNonexistentNorms(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.audit_log = AuditLog(path=Path(self.tmpdir.name) / "audit_log.jsonl")
        self.orchestrator = Orchestrator(audit_log=self.audit_log)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_fabricated_norm_returns_no_verificado(self):
        response = self.orchestrator.answer(
            "Que dice el Decreto Supremo N.º 9999 sobre balcones voladizos en zonas sismicas extremas"
        )
        self.assertTrue(response.no_verificado)
        self.assertEqual(response.resumen, STANDARD_NO_VERIFICADO_MESSAGE)
        self.assertEqual(response.norma_o_documento, [])
        self.assertEqual(response.articulo_seccion_pagina, [])
        self.assertTrue(response.escalamiento_requerido)

    def test_no_verificado_response_is_logged_for_audit(self):
        self.orchestrator.answer("Norma completamente inexistente sobre teletransportacion de materiales")
        entries = self.audit_log.read_all()
        self.assertEqual(len(entries), 1)
        self.assertTrue(entries[0]["no_verificado"])
        self.assertTrue(entries[0]["escalamiento_requerido"])


if __name__ == "__main__":
    unittest.main()
