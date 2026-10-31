import unittest

import tests._pathfix  # noqa: F401
from retrieval.citation import build_citation, build_norma_label
from retrieval.index import load_index
from retrieval.search import SearchFilters, search


class TestCitationAccuracy(unittest.TestCase):
    def setUp(self):
        self.documents = load_index()

    def test_citation_contains_exact_article_number_and_page(self):
        hits = search(self.documents, "plazo tramitacion permiso", filters=SearchFilters(tipo_norma="ley"))
        self.assertTrue(hits, "se esperaba al menos un resultado")
        hit = hits[0]
        citation = build_citation(hit)
        self.assertIn(hit.articulo.numero, citation)
        self.assertIn(str(hit.articulo.pagina), citation)
        self.assertIn(hit.document.version, citation)
        self.assertIn(hit.document.estado_vigencia, citation)

    def test_citation_flags_synthetic_fixtures(self):
        hits = search(self.documents, "accesibilidad", filters=SearchFilters(tipo_norma="reglamento"))
        self.assertTrue(hits)
        citation = build_citation(hits[0])
        self.assertIn("FIXTURE SINTÉTICO DE PRUEBA", citation)

    def test_norma_label_includes_tipo_norma_and_organismo(self):
        hits = search(self.documents, "accesibilidad", filters=SearchFilters(tipo_norma="reglamento"))
        self.assertTrue(hits)
        label = build_norma_label(hits[0])
        self.assertIn("[reglamento]", label)
        self.assertIn(hits[0].document.organismo, label)

    def test_citation_never_invents_article_text(self):
        hits = search(self.documents, "plazo tramitacion permiso", filters=SearchFilters(tipo_norma="ley"))
        for hit in hits:
            # La cita se construye solo desde metadatos del documento cargado,
            # nunca desde texto generado; el número de artículo citado debe
            # existir literalmente en la lista de artículos del documento.
            numeros_reales = [a.numero for a in hit.document.articulos]
            self.assertIn(hit.articulo.numero, numeros_reales)


if __name__ == "__main__":
    unittest.main()
