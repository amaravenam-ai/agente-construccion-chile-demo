import unittest

import tests._pathfix  # noqa: F401
from retrieval.deprecation_detector import check_vigencia, filter_usable_documents
from retrieval.index import load_index


class TestVigencia(unittest.TestCase):
    def setUp(self):
        self.documents = load_index()
        self.by_id = {d.documento_id: d for d in self.documents}

    def test_vigente_document_has_no_alert(self):
        alerta = check_vigencia(self.by_id["doc-fic-002"])
        self.assertEqual(alerta.tipo_alerta, "ninguna")

    def test_modificada_document_has_no_blocking_alert(self):
        alerta = check_vigencia(self.by_id["doc-fic-001"])
        self.assertEqual(alerta.tipo_alerta, "ninguna")
        self.assertEqual(alerta.estado_vigencia, "modificada")

    def test_derogada_document_is_flagged(self):
        alerta = check_vigencia(self.by_id["doc-fic-005"])
        self.assertEqual(alerta.tipo_alerta, "derogada")
        self.assertIn("no debe citarse", alerta.mensaje)

    def test_filter_usable_documents_excludes_derogada(self):
        usable = filter_usable_documents(self.documents)
        usable_ids = {d.documento_id for d in usable}
        self.assertNotIn("doc-fic-005", usable_ids)
        self.assertIn("doc-fic-002", usable_ids)


if __name__ == "__main__":
    unittest.main()
