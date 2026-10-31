"""Capa de seguridad jurídica: bloquea respuestas definitivas sin fuente
y detecta solicitudes de asesoría jurídica personalizada.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

HIGH_STAKES_TOPIC_PATTERNS = [
    re.compile(r"\blitigio\b", re.IGNORECASE),
    re.compile(r"\bsanci[oó]n(es)?\b", re.IGNORECASE),
    re.compile(r"\bmulta(s)?\b", re.IGNORECASE),
    re.compile(r"\bpermiso(s)?\s+de\s+edificaci[oó]n\b", re.IGNORECASE),
    re.compile(r"\brecepci[oó]n\s+(final|definitiva|municipal)\b", re.IGNORECASE),
    re.compile(r"\bdemanda(r)?\b", re.IGNORECASE),
]

PERSONALIZED_ADVICE_PATTERNS = [
    re.compile(r"\bmi\s+caso\b", re.IGNORECASE),
    re.compile(r"\bdeber[íi]a\s+yo\b", re.IGNORECASE),
    re.compile(r"\bqu[ée]\s+debo\s+hacer\b", re.IGNORECASE),
    re.compile(r"\brepres[ée]nt(a|e)me\b", re.IGNORECASE),
    re.compile(r"\bme\s+pueden\s+multar\s+a\s+m[íi]\b", re.IGNORECASE),
    re.compile(r"\bmi\s+contrato\b", re.IGNORECASE),
    re.compile(r"\bmi\s+obra\b", re.IGNORECASE),
]


@dataclass
class PolicyVerdict:
    requiere_escalamiento: bool
    es_solicitud_personalizada: bool
    razones: List[str]


def touches_high_stakes_topic(question: str) -> bool:
    return any(p.search(question) for p in HIGH_STAKES_TOPIC_PATTERNS)


def is_personalized_advice_request(question: str) -> bool:
    return any(p.search(question) for p in PERSONALIZED_ADVICE_PATTERNS)


def evaluate_policy(question: str, has_reliable_sources: bool) -> PolicyVerdict:
    razones: List[str] = []
    personalizada = is_personalized_advice_request(question)
    alto_riesgo = touches_high_stakes_topic(question)

    requiere_escalamiento = False
    if personalizada:
        requiere_escalamiento = True
        razones.append("La pregunta solicita asesoría jurídica personalizada sobre un caso propio.")
    if alto_riesgo and not has_reliable_sources:
        requiere_escalamiento = True
        razones.append("La pregunta toca litigios, sanciones o permisos sin fuentes confiables disponibles.")
    if not has_reliable_sources:
        requiere_escalamiento = True
        razones.append("No hay fuentes confiables suficientes para fundamentar una respuesta definitiva.")

    return PolicyVerdict(
        requiere_escalamiento=requiere_escalamiento,
        es_solicitud_personalizada=personalizada,
        razones=razones,
    )
