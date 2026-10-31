"""Registro de auditoría append-only para cada respuesta emitida por el agente.

Cada entrada sigue schemas/provenance.schema.json. El log es JSON Lines
(un objeto JSON por línea) para permitir escritura incremental sin
reescribir el archivo completo.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

DEFAULT_LOG_PATH = Path(__file__).resolve().parent / "audit_log.jsonl"


@dataclass
class AuditEntry:
    pregunta: str
    documentos_utilizados: List[str]
    hashes: Dict[str, str]
    no_verificado: bool
    escalamiento_requerido: bool
    alertas_seguridad: List[str] = field(default_factory=list)
    timestamp_utc: str = ""
    auditoria_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return {
            "auditoria_id": self.auditoria_id,
            "timestamp_utc": self.timestamp_utc,
            "pregunta": self.pregunta,
            "documentos_utilizados": self.documentos_utilizados,
            "hashes": self.hashes,
            "no_verificado": self.no_verificado,
            "escalamiento_requerido": self.escalamiento_requerido,
            "alertas_seguridad": self.alertas_seguridad,
        }


class AuditLog:
    """Escribe y lee entradas de auditoría en formato JSON Lines."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else DEFAULT_LOG_PATH

    def append(self, entry: AuditEntry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    def read_all(self) -> List[dict]:
        if not self.path.exists():
            return []
        entries = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries
