import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from agent.orchestrator import Orchestrator
from provenance.audit_log import AuditLog
from retrieval.deprecation_detector import check_vigencia
from retrieval.index import load_index


class TestDeprecationDetection(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.audit_log = AuditLog(path=Path(self.tmpdir.name) / "audit_log.jsonl")
        self.orchestrator = Orchestrator(audit_log=self.audit_log)
        self.documents = load_index()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_detector_flags_derogada_state(self):
        derogado = next(d for d in self.documents if d.documento_id == "doc-fic-005")
        alerta = check_vigencia(derogado)
        self.assertEqual(alerta.tipo_alerta, "derogada")

    def test_orchestrator_never_cites_derogated_document(self):
        response = self.orchestrator.answer("subcontratacion")
        self.assertNotIn("doc-fic-005", response.documentos_utilizados)

    def test_orchestrator_logs_deprecation_alert(self):
        self.orchestrator.answer("subcontratacion")
        entries = self.audit_log.read_all()
        alertas = " ".join(entries[-1]["alertas_seguridad"])
        self.assertIn("doc-fic-005", alertas)
        self.assertIn("derogado", alertas)


if __name__ == "__main__":
    unittest.main()
