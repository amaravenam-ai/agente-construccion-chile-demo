import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from agent.orchestrator import Orchestrator
from provenance.audit_log import AuditLog
from security.pii_detector import redact_pii, scan_for_pii


class TestPiiDetector(unittest.TestCase):
    def test_detects_rut(self):
        findings = scan_for_pii("Mi RUT es 12.345.678-9, favor verificar mi permiso.")
        tipos = {f.tipo for f in findings}
        self.assertIn("rut", tipos)

    def test_detects_email(self):
        findings = scan_for_pii("Contactarme a persona.ejemplo@correo.cl por el trámite.")
        tipos = {f.tipo for f in findings}
        self.assertIn("email", tipos)

    def test_detects_chilean_phone(self):
        findings = scan_for_pii("Mi teléfono es +56 9 1234 5678.")
        tipos = {f.tipo for f in findings}
        self.assertIn("telefono", tipos)

    def test_redact_pii_removes_all_findings(self):
        texto = "RUT 12.345.678-9, correo persona@correo.cl, tel +56 9 1234 5678."
        redactado = redact_pii(texto)
        self.assertNotIn("12.345.678-9", redactado)
        self.assertNotIn("persona@correo.cl", redactado)
        self.assertEqual(scan_for_pii(redactado), [])

    def test_no_false_positive_on_plain_legal_text(self):
        texto = "El plazo simulado de tramitación del permiso ficticio será de 20 días hábiles."
        self.assertEqual(scan_for_pii(texto), [])


class TestOrchestratorPiiHandling(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.audit_log = AuditLog(path=Path(self.tmpdir.name) / "audit_log.jsonl")
        self.orchestrator = Orchestrator(audit_log=self.audit_log)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_pii_in_question_is_flagged_in_audit_log(self):
        self.orchestrator.answer("Mi RUT es 12.345.678-9, cual es el plazo del permiso ficticio")
        entries = self.audit_log.read_all()
        alertas = " ".join(entries[-1]["alertas_seguridad"])
        self.assertIn("PII", alertas)


if __name__ == "__main__":
    unittest.main()
