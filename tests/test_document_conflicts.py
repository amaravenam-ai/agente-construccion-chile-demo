import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from agent.orchestrator import Orchestrator
from provenance.audit_log import AuditLog
from retrieval.index import Articulo, Document, load_index


def _make_conflicting_documents():
    doc_a = Document(
        documento_id="doc-test-conflicto-a",
        norma_id="norma-test-conflicto-a",
        source_id="NO_VERIFICADO",
        tipo_norma="circular",
        materia="plazo conflictotest de recepcion",
        organismo="Organismo Ficticio A",
        fecha="2020-01-01",
        estado_vigencia="vigente",
        version="1.0",
        sha256="NO_VERIFICADO",
        path="n/a",
        es_sintetico=True,
        titulo="Circular ficticia A sobre plazo conflictotest",
        articulos=[Articulo(numero="Punto 1", texto="El plazo conflictotest de recepcion es de 10 dias.", pagina="1")],
    )
    doc_b = Document(
        documento_id="doc-test-conflicto-b",
        norma_id="norma-test-conflicto-b",
        source_id="NO_VERIFICADO",
        tipo_norma="circular",
        materia="plazo conflictotest de recepcion",
        organismo="Organismo Ficticio B",
        fecha="2020-06-01",
        estado_vigencia="vigente",
        version="1.0",
        sha256="NO_VERIFICADO",
        path="n/a",
        es_sintetico=True,
        titulo="Circular ficticia B sobre plazo conflictotest",
        articulos=[Articulo(numero="Punto 1", texto="El plazo conflictotest de recepcion es de 45 dias.", pagina="1")],
    )
    return [doc_a, doc_b]


class TestDocumentConflicts(unittest.TestCase):
    """Cuando dos documentos vigentes se contradicen, el agente debe
    exponer ambas fuentes en vez de elegir silenciosamente una."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.audit_log = AuditLog(path=Path(self.tmpdir.name) / "audit_log.jsonl")
        # Se combina con el corpus real de fixtures para que el cálculo de
        # idf tenga suficiente base estadística (ver mismo razonamiento en
        # tests/test_prompt_injection.py).
        self.orchestrator = Orchestrator(
            documents=load_index() + _make_conflicting_documents(),
            audit_log=self.audit_log,
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_both_conflicting_documents_are_surfaced(self):
        response = self.orchestrator.answer("conflictotest")
        self.assertIn("doc-test-conflicto-a", response.documentos_utilizados)
        self.assertIn("doc-test-conflicto-b", response.documentos_utilizados)

    def test_conflict_is_not_presented_as_single_certain_answer(self):
        response = self.orchestrator.answer("conflictotest")
        self.assertNotEqual(response.nivel_confianza, "alto")


if __name__ == "__main__":
    unittest.main()
