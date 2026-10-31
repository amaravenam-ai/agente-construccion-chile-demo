"""Búsqueda determinista por palabra clave con filtros estructurados.

No usa ningún modelo de embeddings ni servicio externo: es coincidencia
léxica con ponderación TF-IDF simple, calculada en memoria a partir del
propio corpus consultado. Todo es explicable: cada score puede
recalcularse a mano a partir de las frecuencias de término.

Limitación conocida (documentada en docs/ARQUITECTURA.md): no hay
normalización morfológica (stemming/lematización), por lo que
singular/plural o variantes de género no siempre coinciden con la
consulta. Se normalizan acentos y mayúsculas, y se descartan
stopwords en español.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional

from retrieval.index import Articulo, Document

_WORD_PATTERN = re.compile(r"\w+", re.UNICODE)

_STOPWORDS = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con", "contra",
    "cual", "cuales", "cuando", "de", "del", "desde", "donde", "durante", "e", "el",
    "ella", "ellas", "ellos", "en", "entre", "era", "erais", "eran", "eras", "eres",
    "es", "esa", "esas", "ese", "esos", "esta", "estas", "este", "esto", "estos",
    "fue", "ha", "han", "hasta", "la", "las", "le", "les", "lo", "los", "mas", "me",
    "mi", "mis", "mucho", "muchos", "muy", "nada", "ni", "no", "nos", "nosotros",
    "o", "os", "otra", "otras", "otro", "otros", "para", "pero", "poco", "por",
    "porque", "que", "quien", "quienes", "se", "sea", "sean", "ser", "si", "sin",
    "sobre", "su", "sus", "te", "tiene", "tienen", "todo", "todos", "tu", "tus",
    "un", "una", "uno", "unos", "y", "ya",
}

# Términos con frecuencia documental por encima de este idf no bastan por sí
# solos para justificar un resultado (evita que palabras de relleno del
# corpus de prueba, como "ficticio"/"simulado", inflen coincidencias).
RELEVANT_IDF_THRESHOLD = 1.3


@dataclass
class SearchFilters:
    materia: Optional[str] = None
    organismo: Optional[str] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    estado_vigencia: Optional[str] = None
    region: Optional[str] = None
    comuna: Optional[str] = None
    tipo_norma: Optional[str] = None


@dataclass
class SearchHit:
    document: Document
    articulo: Articulo
    score: float


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_accents.lower()


def _tokenize(text: str) -> List[str]:
    return _WORD_PATTERN.findall(_normalize(text))


def _matches_filters(doc: Document, filters: SearchFilters) -> bool:
    if filters.materia and filters.materia.lower() not in doc.materia.lower():
        return False
    if filters.organismo and filters.organismo.lower() not in doc.organismo.lower():
        return False
    if filters.estado_vigencia and doc.estado_vigencia != filters.estado_vigencia:
        return False
    if filters.region and (doc.region or "").lower() != filters.region.lower():
        return False
    if filters.comuna and (doc.comuna or "").lower() != filters.comuna.lower():
        return False
    if filters.tipo_norma and doc.tipo_norma != filters.tipo_norma:
        return False
    if filters.fecha_desde and doc.fecha < filters.fecha_desde:
        return False
    if filters.fecha_hasta and doc.fecha > filters.fecha_hasta:
        return False
    return True


def _build_idf(documents: List[Document]) -> Dict[str, float]:
    doc_count = len(documents)
    document_frequency: Counter = Counter()
    for doc in documents:
        terms_in_doc = set()
        texts = [doc.titulo or ""] + [a.texto for a in doc.articulos]
        for text in texts:
            terms_in_doc.update(_tokenize(text))
        for term in terms_in_doc:
            document_frequency[term] += 1

    return {
        term: math.log((1 + doc_count) / (1 + freq)) + 1.0
        for term, freq in document_frequency.items()
    }


def _query_terms(query: str) -> List[str]:
    tokens = _tokenize(query)
    filtered = [t for t in tokens if t not in _STOPWORDS]
    return filtered or tokens


def _weighted_scores(query_terms: List[str], text: str, idf: Dict[str, float]) -> tuple:
    counts = Counter(_tokenize(text))
    total_score = 0.0
    relevant_score = 0.0
    for term in query_terms:
        term_idf = idf.get(term, 1.0)
        contribution = counts.get(term, 0) * term_idf
        total_score += contribution
        if term_idf >= RELEVANT_IDF_THRESHOLD:
            relevant_score += contribution
    return total_score, relevant_score


def search(
    documents: List[Document],
    query: str,
    filters: Optional[SearchFilters] = None,
    limit: int = 10,
) -> List[SearchHit]:
    filters = filters or SearchFilters()
    query_terms = _query_terms(query)
    idf = _build_idf(documents)

    hits: List[SearchHit] = []
    for doc in documents:
        if not _matches_filters(doc, filters):
            continue
        titulo_total, titulo_relevant = _weighted_scores(query_terms, doc.titulo or "", idf)
        for art in doc.articulos:
            art_total, art_relevant = _weighted_scores(query_terms, art.texto, idf)
            total_score = art_total + titulo_total
            relevant_score = art_relevant + titulo_relevant
            if relevant_score > 0:
                hits.append(SearchHit(document=doc, articulo=art, score=total_score))

    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:limit]
