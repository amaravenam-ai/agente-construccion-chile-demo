"""Adaptador LLM SIN PESOS para la fase actual del proyecto.

Compone resúmenes deterministas a partir exclusivamente de los
fragmentos recuperados (context_chunks). No realiza inferencia real,
no descarga ni carga pesos de ningún modelo, y no contacta ningún
servicio externo. Sirve para validar el resto del pipeline (retrieval,
citación, seguridad, formato de respuesta) antes de conectar, en una
fase posterior y bajo autorización independiente, un motor LLM local
real a través de la misma LlmInterface.
"""
from __future__ import annotations

from typing import List

from agent.llm_interface import LlmContextChunk, LlmInterface


class FixtureLlm(LlmInterface):
    def summarize(self, question: str, context_chunks: List[LlmContextChunk]) -> str:
        if not context_chunks:
            return "No se encontraron fragmentos recuperados para responder esta pregunta."

        partes = [f"Sobre la base de {len(context_chunks)} fragmento(s) recuperado(s):"]
        for chunk in context_chunks:
            texto = _strip_data_markers(chunk.text)
            primera_linea = texto.strip().splitlines()[0][:240] if texto.strip() else ""
            partes.append(f"- {chunk.label}: {primera_linea}")
        return " ".join(partes)


def _strip_data_markers(text: str) -> str:
    lines = [
        line
        for line in text.splitlines()
        if not line.startswith("<<<DATOS_RECUPERADOS") and not line.startswith("<<<FIN_DATOS_RECUPERADOS")
    ]
    return "\n".join(lines)
