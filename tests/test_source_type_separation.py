import unittest

import tests._pathfix  # noqa: F401
from retrieval.index import load_index


class TestSourceTypeSeparation(unittest.TestCase):
    """La ley, el reglamento, la circular, el dictamen (asimilable a una
    opinión administrativa) y la jurisprudencia tienen distinto valor
    normativo y no deben presentarse como equivalentes."""

    def setUp(self):
        self.documents = load_index()

    def test_fixture_corpus_covers_distinct_tipos_norma(self):
        tipos = {d.tipo_norma for d in self.documents}
        self.assertEqual(
            tipos,
            {"ley", "reglamento", "circular", "dictamen", "jurisprudencia"},
        )

    def test_response_schema_enumerates_opinion_as_separate_type(self):
        # El esquema documental soporta 'opinion' como tipo distinto aunque
        # todavía no haya un fixture cargado de ese tipo; ver
        # schemas/document_manifest.schema.json.
        import json
        from pathlib import Path

        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "document_manifest.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        tipo_norma_enum = schema["properties"]["tipo_norma"]["enum"]
        for tipo in ("ley", "reglamento", "circular", "dictamen", "jurisprudencia", "opinion"):
            self.assertIn(tipo, tipo_norma_enum)

    def test_dictamen_is_not_confused_with_jurisprudencia(self):
        dictamen = next(d for d in self.documents if d.documento_id == "doc-fic-006")
        jurisprudencia = next(d for d in self.documents if d.documento_id == "doc-fic-007")
        self.assertEqual(dictamen.tipo_norma, "dictamen")
        self.assertEqual(jurisprudencia.tipo_norma, "jurisprudencia")
        self.assertNotEqual(dictamen.tipo_norma, jurisprudencia.tipo_norma)


if __name__ == "__main__":
    unittest.main()
