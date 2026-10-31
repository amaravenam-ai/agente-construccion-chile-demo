"""Detección y redacción de datos personales (PII) en preguntas y documentos.

Evita almacenar RUT, direcciones o datos de clientes sin autorización
explícita, conforme a la restricción de seguridad del agente.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

RUT_PATTERN = re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b")
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_CL_PATTERN = re.compile(r"\b(?:\+?56)?\s?9\s?\d{4}\s?\d{4}\b")


@dataclass
class PiiFinding:
    tipo: str
    fragmento: str


def scan_for_pii(text: str) -> List[PiiFinding]:
    findings: List[PiiFinding] = []
    for match in RUT_PATTERN.finditer(text):
        findings.append(PiiFinding(tipo="rut", fragmento=match.group()))
    for match in EMAIL_PATTERN.finditer(text):
        findings.append(PiiFinding(tipo="email", fragmento=match.group()))
    for match in PHONE_CL_PATTERN.finditer(text):
        findings.append(PiiFinding(tipo="telefono", fragmento=match.group()))
    return findings


def redact_pii(text: str) -> str:
    redacted = RUT_PATTERN.sub("[RUT REDACTADO]", text)
    redacted = EMAIL_PATTERN.sub("[EMAIL REDACTADO]", redacted)
    redacted = PHONE_CL_PATTERN.sub("[TELÉFONO REDACTADO]", redacted)
    return redacted
