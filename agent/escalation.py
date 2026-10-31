"""Recomendaciones de escalamiento a revisión profesional."""
from __future__ import annotations

PROFESSIONAL_BY_TOPIC = {
    "estructural": "un calculista o ingeniero estructural",
    "seguridad": "un prevencionista de riesgos",
    "permiso": "la Dirección de Obras Municipales (DOM) competente",
    "contrato": "un abogado especializado en construcción",
    "subcontratacion": "un abogado laboral",
    "subcontratación": "un abogado laboral",
    "accesibilidad": "un arquitecto especializado en accesibilidad universal",
    "energ": "un especialista en eficiencia energética",
}

DEFAULT_RECOMMENDATION = (
    "Consulte a un abogado, arquitecto, calculista, prevencionista de riesgos o a la Dirección de "
    "Obras Municipales (DOM) competente, según corresponda a su situación específica."
)


def recommend_professional(materia: str) -> str:
    materia_lower = materia.lower()
    for keyword, profesional in PROFESSIONAL_BY_TOPIC.items():
        if keyword in materia_lower:
            return f"Se recomienda consultar con {profesional} antes de tomar decisiones."
    return DEFAULT_RECOMMENDATION
