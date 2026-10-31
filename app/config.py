"""Configuración central del agente. Solo constantes, sin secretos."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_MANIFEST_PATH = REPO_ROOT / "documents" / "manifest.json"
SOURCES_REGISTRY_PATH = REPO_ROOT / "sources" / "fuentes_aprobadas.json"
AUDIT_LOG_PATH = REPO_ROOT / "provenance" / "audit_log.jsonl"

AGENT_NAME = "Amalan Agente de Construcción Chile"
AGENT_STAGE = "fase_inicial_fixtures_sinteticos"
BASE_MODEL_AUTORIZADO_FUTURO = "meta-llama/Llama-3.1-8B"
