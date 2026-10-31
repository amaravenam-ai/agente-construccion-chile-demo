import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from agent.orchestrator import Orchestrator
from provenance.audit_log import AuditLog
from retrieval.index import load_index
from retrieval.search import SearchFilters, search


class TestNonBindingJurisprudence(unittest.TestCase):
    def setUp(self):
        self.documents = load_index()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.audit_log = AuditLog(path=Path(self.tmpdir.name) / "audit_log.jsonl")
        self.orchestrator = Orchestrator(audit_log=self.audit_log)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_fixture_jurisprudencia_is_marked_non_binding(self):
        doc = next(d for d in self.documents if d.documento_id == "doc-fic-007")
        self.assertEqual(doc.tipo_norma, "jurisprudencia")
        self.assertIs(doc.vinculante, False)

    def test_search_can_filter_by_tipo_norma_jurisprudencia(self):
        hits = search(self.documents, "sentencia contrato construccion", filters=SearchFilters(tipo_norma="jurisprudencia"))
        self.assertTrue(hits)
        self.assertTrue(all(h.document.tipo_norma == "jurisprudencia" for h in hits))

    def test_response_warns_jurisprudencia_is_not_binding(self):
        response = self.orchestrator.answer(
            "Que dice la sentencia ficticia sobre incumplimiento de contrato de construccion",
            filters=SearchFilters(tipo_norma="jurisprudencia"),
        )
        self.assertFalse(response.no_verificado)
        texto_riesgos = " ".join(response.riesgos_informacion_faltante)
        self.assertIn("NO VINCULANTE", texto_riesgos)


if __name__ == "__main__":
    unittest.main()
