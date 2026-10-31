import unittest

import tests._pathfix  # noqa: F401
from retrieval.index import load_index
from retrieval.version_compare import compare_versions, find_versions


class TestVersionComparison(unittest.TestCase):
    def setUp(self):
        self.documents = load_index()

    def test_find_versions_returns_both_versions_sorted(self):
        versiones = find_versions(self.documents, "norma-fic-edificacion")
        self.assertEqual([d.version for d in versiones], ["1.0", "2.0"])

    def test_compare_versions_detects_modified_articles(self):
        v1, v2 = find_versions(self.documents, "norma-fic-edificacion")
        comparison = compare_versions(v1, v2)
        cambios = {d.numero: d.cambio for d in comparison.diffs}
        self.assertEqual(cambios["Artículo 1 (ficticio)"], "modificado")
        self.assertEqual(cambios["Artículo 2 (ficticio)"], "modificado")

    def test_compare_versions_detects_added_article(self):
        v1, v2 = find_versions(self.documents, "norma-fic-edificacion")
        comparison = compare_versions(v1, v2)
        cambios = {d.numero: d.cambio for d in comparison.diffs}
        self.assertEqual(cambios["Artículo 3 (ficticio, nuevo)"], "agregado")

    def test_compare_versions_rejects_different_normas(self):
        docs_by_id = {d.documento_id: d for d in self.documents}
        with self.assertRaises(ValueError):
            compare_versions(docs_by_id["doc-fic-002"], docs_by_id["doc-fic-003"])


if __name__ == "__main__":
    unittest.main()
