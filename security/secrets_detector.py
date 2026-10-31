"""Detección de secretos y credenciales en texto de entrada o documentos."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic_api_key": re.compile(r"\b(?:sk|pk|api[_-]?key)[_-][A-Za-z0-9]{16,}\b", re.IGNORECASE),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9\-_.]{20,}\b"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "password_assignment": re.compile(r"\b(password|contrase[ñn]a|clave)\s*[:=]\s*\S+", re.IGNORECASE),
}


@dataclass
class SecretFinding:
    tipo: str
    fragmento: str


def scan_for_secrets(text: str) -> List[SecretFinding]:
    findings: List[SecretFinding] = []
    for tipo, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append(SecretFinding(tipo=tipo, fragmento=match.group()))
    return findings


def contains_secret(text: str) -> bool:
    return len(scan_for_secrets(text)) > 0
