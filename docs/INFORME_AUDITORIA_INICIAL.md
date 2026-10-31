# Informe de auditoría inicial

**Fecha del informe:** 2026-07-19
**Alcance:** estado del repositorio `Amalan-Agente-Construccion-Chile` al
finalizar la construcción de la fase inicial (fixtures sintéticos, sin
ingesta de contenido legal real).

## Resumen ejecutivo

El repositorio implementa un agente híbrido (retrieval + LLM sin pesos +
capa de seguridad jurídica) funcional end-to-end sobre un corpus
**enteramente sintético**. Todos los comandos reproducibles listados en
[RUNBOOK.md](RUNBOOK.md) se ejecutaron y verificaron durante esta auditoría.
No hay ninguna fuente jurídica real verificada ni ingerida. El sistema no
debe usarse para asesorar decisiones reales — ver
[BLOQUEADORES.md](BLOQUEADORES.md).

## Resultados verificados en esta auditoría

| Verificación | Comando | Resultado |
|---|---|---|
| Estructura de carpetas | `python scripts/run_audit.py` | 13/13 carpetas requeridas presentes |
| Integridad de hashes documentales | `python scripts/verify_manifest.py` | 7/7 documentos con hash coincidente |
| Bloqueo de ingesta sin derechos verificados | `python scripts/ingest_approved_sources.py` | 7/7 fuentes correctamente `BLOQUEADA` (0 aprobadas) |
| Harness de evaluación funcional | `python evaluation/run_eval.py` | 6/6 casos aprobados |
| Suite de pruebas unitarias | `python -m unittest discover -s tests -v` | 55/55 pruebas aprobadas |

## Cobertura de la suite de pruebas por categoría exigida

| Categoría exigida | Archivo(s) de prueba |
|---|---|
| Exactitud de citas | `tests/test_citation_accuracy.py` |
| Vigencia normativa | `tests/test_vigencia.py` |
| Rechazo de normas inexistentes | `tests/test_reject_nonexistent_norms.py` |
| Detección de derogación | `tests/test_deprecation_detection.py` |
| Comparación de versiones | `tests/test_version_comparison.py` |
| Separación ley/reglamento/circular/opinión | `tests/test_source_type_separation.py` |
| Prompt injection | `tests/test_prompt_injection.py` |
| PII | `tests/test_pii.py` |
| Respuestas sin fuente | `tests/test_no_source_response.py` |
| Preguntas ambiguas | `tests/test_ambiguous_queries.py` |
| Conflictos entre documentos | `tests/test_document_conflicts.py` |
| Jurisprudencia no vinculante | `tests/test_non_binding_jurisprudence.py` |
| Solicitudes de asesoría personalizada | `tests/test_personalized_advice_request.py` |
| (Adicional) Verificación de hashes y secretos | `tests/test_secrets_and_hashes.py` |
| (Adicional) Verificación de derechos de fuentes | `tests/test_rights_verifier.py` |

## Hallazgos

### Corregidos durante la construcción de esta fase

- **Retrieval demasiado permisivo.** La primera versión de
  `retrieval/search.py` contaba coincidencias literales sin filtrar
  stopwords ni ponderar por relevancia; dado que los fixtures de prueba
  repiten palabras como "ficticio"/"simulado" en casi todos los documentos,
  una consulta genérica devolvía prácticamente todo el corpus. Se corrigió
  agregando normalización de acentos, filtrado de stopwords en español y
  ponderación TF-IDF con un umbral mínimo de relevancia
  (`RELEVANT_IDF_THRESHOLD`). Verificado con `evaluation/run_eval.py` y
  `tests/test_ambiguous_queries.py`.
- **Aserciones de evaluación frágiles.** Los primeros casos de
  `evaluation/eval_cases/` verificaban la presencia de un `documento_id`
  buscándolo como substring dentro de las etiquetas de cita (que nunca
  contienen ese id). Se agregó el campo interno
  `StructuredResponse.documentos_utilizados` (no forma parte del contrato
  externo `schemas/response.schema.json`) para que pruebas y evaluación
  verifiquen procedencia exacta sin depender de texto libre.

### Abiertos (no bloquean esta fase, sí bloquean producción)

Ver la lista completa y priorizada en [BLOQUEADORES.md](BLOQUEADORES.md).
En resumen: cero fuentes verificadas, cero documentos reales, sin motor LLM
conectado, sin revisión profesional del dominio legal, sin normalización
morfológica en el retrieval, sin revisión de seguridad independiente.

## Alcance NO cubierto por esta auditoría

- No se evaluó exactitud jurídica de ningún contenido, porque no existe
  contenido jurídico real en el repositorio.
- No se realizó pentesting ni revisión de seguridad por terceros.
- No se midió cobertura normativa (no aplica: cobertura real actual es
  cero documentos legales verificados).
- No se evaluó rendimiento ni escalabilidad — el volumen actual (7
  fixtures) no es representativo de un corpus de producción.

## Adenda — 2026-07-20

Este informe describe el estado al 2026-07-19; los números de esta tabla
son una fotografía de ese momento y no se reescriben. Cambios posteriores
relevantes (ver `python scripts/run_audit.py` para el estado recalculado
en cualquier momento):

- Se investigaron derechos de las 6 fuentes institucionales restantes
  (además de `src-leychile-bcn`) y se corroboró el Art. 88 de la Ley
  17.336 (titularidad estatal por defecto sobre obras de funcionarios) —
  ver `docs/FUENTES_APROBADAS.md`.
- Se agregó `sources/cobertura_objetivo.json` (18 normas/áreas
  específicas objetivo) y `scripts/coverage_report.py`.
- Se agregó `scripts/add_verified_document.py`, la única vía prevista
  para ingesta real, con el gate de derechos embebido.
- Se registró una octava fuente institucional, `src-sea` (Servicio de
  Evaluación Ambiental), sin investigar todavía.
- La suite de pruebas creció de 55 a 70 pruebas (`tests/test_cobertura_objetivo.py`,
  `tests/test_add_verified_document.py`).
- Se agregó `docs/SOLICITUDES_PENDIENTES.md` con borradores de contacto
  institucional.

Ninguno de estos cambios ingirió contenido legal real ni aprobó ninguna
fuente; el estado de fondo sigue siendo el mismo que describe este
informe.
