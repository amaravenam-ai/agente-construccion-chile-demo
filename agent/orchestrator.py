"""Orquestador del agente: une retrieval, seguridad, citación y respuesta.

Flujo por pregunta:
1. Escanear la pregunta en busca de PII/secretos (no bloquea, pero se
   registra en la auditoría y se evita persistir texto plano innecesario).
2. Recuperar candidatos con retrieval.search.
3. Descartar documentos derogados/ambiguos (retrieval.deprecation_detector)
   y fragmentos con posible prompt injection (security.prompt_injection_guard).
4. Si no quedan documentos utilizables, responder con el mensaje NO
   VERIFICADO estándar y marcar escalamiento obligatorio.
5. Si quedan documentos, construir citas exactas, pedir al adaptador LLM
   (sin pesos) un resumen basado solo en esos fragmentos, aplicar la
   política de escalamiento y devolver la respuesta estructurada.
6. Registrar cada respuesta en el log de auditoría (provenance/audit_log).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from agent.escalation import recommend_professional
from agent.fixture_llm import FixtureLlm
from agent.llm_interface import LlmContextChunk, LlmInterface
from agent.response_builder import STANDARD_DISCLAIMER, StructuredResponse, build_no_verificado_response
from provenance.audit_log import AuditEntry, AuditLog
from retrieval.citation import build_citation, build_norma_label
from retrieval.deprecation_detector import check_vigencia
from retrieval.index import Document, load_index
from retrieval.search import SearchFilters, SearchHit, search
from security.pii_detector import scan_for_pii
from security.policy import evaluate_policy
from security.prompt_injection_guard import scan_for_injection, wrap_as_data
from security.secrets_detector import scan_for_secrets


class Orchestrator:
    def __init__(
        self,
        llm: Optional[LlmInterface] = None,
        documents: Optional[List[Document]] = None,
        audit_log: Optional[AuditLog] = None,
    ):
        self.llm = llm or FixtureLlm()
        self.documents = documents if documents is not None else load_index()
        self.audit_log = audit_log or AuditLog()

    def answer(
        self,
        question: str,
        filters: Optional[SearchFilters] = None,
        fecha_consulta: str = "",
    ) -> StructuredResponse:
        auditoria_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        fecha_consulta = fecha_consulta or timestamp[:10]

        alertas_seguridad: List[str] = []

        if scan_for_pii(question):
            alertas_seguridad.append("PII detectada en la pregunta del usuario.")
        if scan_for_secrets(question):
            alertas_seguridad.append("Posible secreto/credencial detectado en la pregunta del usuario.")

        hits: List[SearchHit] = search(self.documents, question, filters=filters)
        usable_hits: List[SearchHit] = []
        for hit in hits:
            vigencia = check_vigencia(hit.document)
            if vigencia.tipo_alerta != "ninguna":
                alertas_seguridad.append(f"{hit.document.documento_id}: {vigencia.mensaje}")
                continue
            if scan_for_injection(hit.articulo.texto):
                alertas_seguridad.append(
                    f"{hit.document.documento_id}: posible intento de prompt injection en el texto "
                    "recuperado; fragmento excluido del contexto del LLM."
                )
                continue
            usable_hits.append(hit)

        has_reliable_sources = len(usable_hits) > 0
        policy_verdict = evaluate_policy(question, has_reliable_sources)

        documentos_utilizados = [hit.document.documento_id for hit in usable_hits]
        hashes = {hit.document.documento_id: hit.document.sha256 for hit in usable_hits}

        if not has_reliable_sources:
            response = build_no_verificado_response(
                fecha_consulta=fecha_consulta,
                riesgos=policy_verdict.razones or ["No se recuperó ningún documento relevante para esta pregunta."],
                auditoria_id=auditoria_id,
            )
            self._log(auditoria_id, timestamp, question, documentos_utilizados, hashes, True, True, alertas_seguridad)
            return response

        context_chunks = [
            LlmContextChunk(
                label=build_norma_label(hit),
                text=wrap_as_data(hit.document.documento_id, hit.articulo.texto),
            )
            for hit in usable_hits
        ]
        resumen = self.llm.summarize(question, context_chunks)

        citas = [build_citation(hit) for hit in usable_hits]
        normas = [build_norma_label(hit) for hit in usable_hits]
        materias = ", ".join(sorted({hit.document.materia for hit in usable_hits}))
        vigencias = "; ".join(sorted({f"{hit.document.documento_id}: {hit.document.estado_vigencia}" for hit in usable_hits}))

        supuestos = ["La respuesta se basa únicamente en los fragmentos recuperados y citados abajo."]
        if any(hit.document.es_sintetico for hit in usable_hits):
            supuestos.append("Uno o más documentos usados son FIXTURES SINTÉTICOS DE PRUEBA, no texto legal real.")

        riesgos = list(policy_verdict.razones)
        no_vinculantes = [
            hit.document.documento_id
            for hit in usable_hits
            if hit.document.tipo_norma == "jurisprudencia" and hit.document.vinculante is False
        ]
        if no_vinculantes:
            riesgos.append(
                f"Incluye jurisprudencia NO VINCULANTE ({', '.join(no_vinculantes)}); no debe tratarse "
                "como precedente obligatorio."
            )

        tipos_norma_usados = {hit.document.tipo_norma for hit in usable_hits}
        if len(tipos_norma_usados) > 1:
            riesgos.append(
                f"La respuesta combina distintos tipos de fuente ({', '.join(sorted(tipos_norma_usados))}); "
                "ley, reglamento, circular, dictamen y jurisprudencia tienen distinto valor normativo."
            )

        nivel_confianza = "medio" if any(hit.document.es_sintetico for hit in usable_hits) else "alto"
        if policy_verdict.requiere_escalamiento:
            nivel_confianza = "bajo"

        response = StructuredResponse(
            resumen=resumen,
            jurisdiccion="Chile",
            fecha_consulta=fecha_consulta,
            norma_o_documento=normas,
            articulo_seccion_pagina=citas,
            vigencia_conocida=vigencias,
            nivel_confianza=nivel_confianza,
            supuestos=supuestos,
            riesgos_informacion_faltante=riesgos,
            advertencia=STANDARD_DISCLAIMER,
            recomendacion=recommend_professional(materias),
            no_verificado=False,
            escalamiento_requerido=policy_verdict.requiere_escalamiento,
            auditoria_id=auditoria_id,
            documentos_utilizados=documentos_utilizados,
        )

        self._log(
            auditoria_id,
            timestamp,
            question,
            documentos_utilizados,
            hashes,
            False,
            policy_verdict.requiere_escalamiento,
            alertas_seguridad,
        )
        return response

    def _log(
        self,
        auditoria_id: str,
        timestamp: str,
        question: str,
        documentos_utilizados: List[str],
        hashes: dict,
        no_verificado: bool,
        escalamiento_requerido: bool,
        alertas_seguridad: List[str],
    ) -> None:
        entry = AuditEntry(
            pregunta=question,
            documentos_utilizados=documentos_utilizados,
            hashes=hashes,
            no_verificado=no_verificado,
            escalamiento_requerido=escalamiento_requerido,
            alertas_seguridad=alertas_seguridad,
            timestamp_utc=timestamp,
            auditoria_id=auditoria_id,
        )
        self.audit_log.append(entry)
