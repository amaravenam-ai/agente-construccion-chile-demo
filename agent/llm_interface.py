"""Interfaz abstracta para motores LLM locales.

Ninguna implementación concreta incluida en este repositorio contiene
pesos de modelo. Esta interfaz permite intercambiar adaptadores
(fixture de prueba, futuro runtime local llama.cpp, etc.) sin acoplar
el resto del agente a un motor específico.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class LlmContextChunk:
    label: str
    text: str


class LlmInterface(ABC):
    @abstractmethod
    def summarize(self, question: str, context_chunks: List[LlmContextChunk]) -> str:
        """Compone una respuesta en lenguaje natural usando SOLO context_chunks.

        Implementaciones reales deben negarse a introducir hechos que no
        estén presentes en context_chunks.
        """
        raise NotImplementedError
