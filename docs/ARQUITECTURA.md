# Arquitectura

## Principio rector

El agente **no depende de que un LLM memorice la legislación**. El LLM
(hoy: `agent/fixture_llm.py`, un adaptador sin pesos) solo tiene permitido
componer lenguaje natural a partir de fragmentos ya recuperados y citados
deterministamente por `retrieval/`. Cualquier motor LLM real que se conecte
en el futuro debe respetar la misma regla a través de `agent/llm_interface.py`.

## Flujo de una pregunta (`agent/orchestrator.py`)

1. **Seguridad de entrada.** `security/pii_detector.py` y
   `security/secrets_detector.py` escanean la pregunta. No bloquean la
   consulta, pero cualquier hallazgo queda en el log de auditoría
   (`provenance/audit_log.py`) para trazabilidad, sin persistir el dato en
   texto plano más de lo necesario.
2. **Recuperación.** `retrieval/search.py` busca en el índice cargado por
   `retrieval/index.py` (desde `documents/manifest.json`). Es una búsqueda
   léxica con ponderación TF-IDF calculada en memoria sobre el propio
   corpus consultado — sin embeddings, sin servicios externos. Soporta
   filtros por materia, organismo, fecha, vigencia, región, comuna y tipo de
   norma (`retrieval/search.py:SearchFilters`).
3. **Filtro de vigencia.** `retrieval/deprecation_detector.py` descarta
   documentos `derogada`, `proyecto` o `no_verificada` antes de que lleguen
   al LLM. Ningún documento derogado se cita jamás como vigente.
4. **Filtro de prompt injection.** `security/prompt_injection_guard.py`
   escanea el texto de cada artículo recuperado. Si detecta frases del tipo
   "ignora las instrucciones anteriores", ese fragmento se descarta del
   contexto y se registra la alerta. El contenido que sí pasa se envuelve
   con `wrap_as_data()`, marcadores explícitos que el adaptador LLM debe
   tratar siempre como datos, nunca como instrucciones.
5. **Si no queda ningún documento utilizable**, la respuesta es
   exactamente el mensaje `NO VERIFICADO` estándar
   (`agent/response_builder.py:STANDARD_NO_VERIFICADO_MESSAGE`), con
   `escalamiento_requerido=true`.
6. **Citación exacta.** `retrieval/citation.py` construye cada cita
   directamente desde los metadatos del `Document`/`Articulo` cargado — el
   número de artículo, la página y el estado de vigencia nunca se generan,
   se leen literalmente del fixture/manifiesto.
7. **Resumen.** `agent/fixture_llm.py` compone una oración por fragmento
   recuperado. No añade hechos que no estén en el contexto.
8. **Política de escalamiento.** `security/policy.py` decide
   `escalamiento_requerido` según: (a) si la pregunta pide asesoría
   personalizada ("mi caso", "mi obra", "qué debo hacer"), (b) si toca temas
   de alto riesgo (litigios, sanciones, permisos) sin fuentes suficientes, o
   (c) si no hay fuentes confiables en absoluto.
9. **Respuesta estructurada.** `agent/response_builder.py` arma el objeto
   final según `schemas/response.schema.json`.
10. **Auditoría.** Cada respuesta (incluidas las `NO VERIFICADO`) se
    registra en `provenance/audit_log.jsonl` con id de auditoría, timestamp
    UTC, documentos usados, sus hashes SHA-256, y las alertas de seguridad
    generadas.

## Por qué TF-IDF y no embeddings

Esta fase no incluye pesos de ningún modelo (ni de embeddings). Una
búsqueda léxica con ponderación por frecuencia inversa de documento es
determinista, auditable a mano y suficiente para el volumen actual de
fixtures. Cuando exista un corpus real aprobado, este módulo puede
reemplazarse o complementarse sin tocar `agent/` ni `security/`, siempre
que seguir cumpliendo el contrato de `retrieval/search.py:SearchHit`.

**Limitación conocida**: no hay normalización morfológica (stemming). Se
normalizan acentos y mayúsculas y se descartan stopwords en español, pero
singular/plural o variantes de género pueden no coincidir exactamente con
la consulta. Ver `retrieval/search.py` para el detalle del algoritmo y su
umbral de relevancia (`RELEVANT_IDF_THRESHOLD`), que evita que palabras de
relleno repetidas en todo el corpus de prueba (p. ej. "ficticio",
"simulado") inflen coincidencias irrelevantes.

## Interfaz LLM sin pesos (`agent/llm_interface.py`, `agent/fixture_llm.py`)

`LlmInterface` es abstracta. La única implementación incluida,
`FixtureLlm`, no realiza inferencia real: concatena y recorta
deterministamente los fragmentos ya citados. Esto permite validar todo el
pipeline (retrieval, seguridad, formato) antes de conectar, en una fase
posterior y bajo autorización independiente, un motor LLM local real (ver
`docs/ALCANCE_LEGAL.md` sobre el único modelo base contemplado).

### Siguiente fase: conexión del motor real (no iniciada)

La conexión de un motor LLM local real es una fase **separada y
posterior**, explícitamente fuera de alcance mientras el usuario no tenga
el motor listo (decisión del usuario, no una limitación técnica de este
repositorio). Cuando corresponda, el trabajo se limita a:

1. Implementar una nueva clase que cumpla `LlmInterface`
   (`agent/llm_interface.py`) — por ejemplo `LocalEngineLlm` — que llame al
   motor real en vez de concatenar texto como hace `FixtureLlm`.
2. Sustituir `FixtureLlm()` por esa implementación en
   `agent/orchestrator.py:Orchestrator.__init__` (un único punto de
   inyección).
3. **No se necesita tocar** `retrieval/`, `security/`, ni el formato de
   respuesta: el contrato ya está definido por `LlmContextChunk` y por la
   regla de que el LLM solo puede usar lo que ya viene citado y filtrado
   por seguridad — el motor real debe respetar la misma regla.
4. Esto sigue condicionado a que existan fuentes con derechos verificados
   (ver más abajo); conectar un motor real no habilita por sí solo el uso
   de contenido no verificado.

## Procedencia y verificación de derechos

- `sources/fuentes_aprobadas.json`: registro de **fuentes institucionales**
  candidatas (7 portales). Todas están `NO_VERIFICADO` o `rechazado` en
  esta fase — ver `docs/FUENTES_APROBADAS.md` para el detalle por fuente.
- `sources/cobertura_objetivo.json`: registro de **normas y áreas
  específicas** (LGUC, OGUC, circulares DDU, Ley de subcontratación, etc.)
  que definen el alcance completo que el agente debería cubrir
  eventualmente — más granular que las 8 fuentes institucionales. Ejecutar
  `scripts/coverage_report.py` para ver el avance.
- `rights/verifier.py`: una fuente solo puede pasar a ingesta si sus tres
  permisos (entrenamiento, uso comercial, derivados) están explícitamente
  en `"si"` y su estado de verificación es `"verificado"`. Ejecutar
  `scripts/ingest_approved_sources.py` muestra el bloqueo activo.
- `scripts/add_verified_document.py`: única vía prevista para agregar un
  documento real a `documents/manifest.json`. El gate de derechos está
  embebido en la propia herramienta (no en un paso separado que se puede
  olvidar) — rechaza automáticamente cualquier documento cuya fuente no
  esté aprobada en `rights/`.
- `documents/manifest.json`: cada documento declara su hash SHA-256 y si es
  `es_sintetico`. `scripts/verify_manifest.py` recalcula los hashes y falla
  si algo no coincide con lo registrado.

## Capa de seguridad jurídica (`security/policy.py`)

No es un filtro de contenido genérico: es una política específica de
dominio legal que:
- Nunca permite que el sistema dé una respuesta "definitiva" sobre
  litigios, sanciones o permisos si no hay fuente confiable.
- Detecta lenguaje de asesoría personalizada en primera persona y fuerza
  escalamiento aunque existan documentos relevantes.
- Se ejecuta siempre, tanto en el camino `NO_VERIFICADO` como en el camino
  con fuentes.
