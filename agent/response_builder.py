"""Construcción de la respuesta estructurada obligatoria del agente."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

STANDARD_NO_VERIFICADO_MESSAGE = (
    "NO VERIFICADO: no existe evidencia documental suficiente para responder con seguridad."
)

STANDARD_DISCLAIMER = (
    "Esta respuesta es generada por un sistema de apoyo informativo y NO sustituye la asesoría de un "
    "abogado, arquitecto, calculista, prevencionista de riesgos o la Dirección de Obras Municipales "
    "(DOM) competente. Verifique siempre con la fuente oficial vigente."
)


@dataclass
class StructuredResponse:
    resumen: str
    jurisdiccion: str
    fecha_consulta: str
    norma_o_documento: List[str]
    articulo_seccion_pagina: List[str]
    vigencia_conocida: str
    nivel_confianza: str
    supuestos: List[str]
    riesgos_informacion_faltante: List[str]
    advertencia: str
    recomendacion: str
    no_verificado: bool
    escalamiento_requerido: bool = False
    auditoria_id: str = ""
    # Identificadores exactos de documents/manifest.json usados. No forma parte
    # del contrato externo (schemas/response.schema.json); existe para que
    # pruebas y auditoría internas verifiquen procedencia sin parsear texto libre.
    documentos_utilizados: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "resumen": self.resumen,
            "jurisdiccion": self.jurisdiccion,
            "fecha_consulta": self.fecha_consulta,
            "norma_o_documento": self.norma_o_documento,
            "articulo_seccion_pagina": self.articulo_seccion_pagina,
            "vigencia_conocida": self.vigencia_conocida,
            "nivel_confianza": self.nivel_confianza,
            "supuestos": self.supuestos,
            "riesgos_informacion_faltante": self.riesgos_informacion_faltante,
            "advertencia": self.advertencia,
            "recomendacion": self.recomendacion,
            "no_verificado": self.no_verificado,
            "escalamiento_requerido": self.escalamiento_requerido,
            "auditoria_id": self.auditoria_id,
        }


def build_no_verificado_response(
    fecha_consulta: str,
    riesgos: List[str],
    auditoria_id: str = "",
) -> StructuredResponse:
    return StructuredResponse(
        resumen=STANDARD_NO_VERIFICADO_MESSAGE,
        jurisdiccion="Chile",
        fecha_consulta=fecha_consulta,
        norma_o_documento=[],
        articulo_seccion_pagina=[],
        vigencia_conocida="NO_VERIFICADO",
        nivel_confianza="no_verificado",
        supuestos=[],
        riesgos_informacion_faltante=riesgos,
        advertencia=STANDARD_DISCLAIMER,
        recomendacion=(
            "Consulte a un abogado, arquitecto, calculista, prevencionista de riesgos o a la DOM "
            "competente para obtener una respuesta fundada."
        ),
        no_verificado=True,
        escalamiento_requerido=True,
        auditoria_id=auditoria_id,
    )
