# Alcance legal y limitaciones

## Este agente NO es

- Un abogado ni un estudio jurídico.
- Un sustituto de la asesoría de un abogado, arquitecto, calculista
  estructural, prevencionista de riesgos o de la Dirección de Obras
  Municipales (DOM) competente.
- Una fuente de verdad completa sobre "todas las leyes de Chile". Solo
  puede citar lo que exista, verificado, en su índice documental.
- Un sistema de decisión automática sobre litigios, sanciones, multas o
  aprobación/rechazo de permisos.

## Estado actual del corpus (fase inicial)

Todo el contenido en `documents/synthetic/` es **ficticio**, creado por
Amalan exclusivamente para probar el pipeline técnico (recuperación,
citación, control de vigencia, seguridad). Ningún fragmento de LGUC, OGUC,
circulares DDU, dictámenes de Contraloría, jurisprudencia real ni normas
NCh ha sido copiado a este repositorio. Cada fixture sintético incluye un
campo `aviso` explícito y la marca `es_sintetico: true` en
`documents/manifest.json`.

Antes de que este agente pueda responder con normativa chilena real, se
requiere, para cada fuente en `sources/fuentes_aprobadas.json`:

1. Verificación humana de los términos de uso/licencia reales de la fuente.
2. Registro de esa verificación en `rights/` según
   `schemas/rights.schema.json`, con evidencia concreta (no
   `NO_VERIFICADO`).
3. Los tres permisos (entrenamiento, uso comercial, derivados) en `"si"`
   explícito.
4. Solo entonces `scripts/ingest_approved_sources.py` dejaría de bloquear
   esa fuente para ingesta real.

Ver [FUENTES_APROBADAS.md](FUENTES_APROBADAS.md) para el detalle
institución por institución, y [BLOQUEADORES.md](BLOQUEADORES.md) para la
lista de lo que falta antes de producción.

## Modelo base

En esta fase no hay pesos de ningún modelo en el repositorio. El único
modelo base que este proyecto contempla adoptar en el futuro, bajo
autorización independiente, acceso aprobado y manifiesto de derechos
válido, es `meta-llama/Llama-3.1-8B`. Si se adapta ese modelo:

- Debe conservarse su procedencia (nombre, versión, licencia de origen) en
  toda documentación y metadatos del sistema.
- No debe describirse como "entrenado desde cero" ni como "100% Amalan".
- Debe mantenerse trazabilidad de qué capas o adaptadores son de Amalan y
  cuáles provienen del modelo base.

No se contempla el uso de Qwen, otras variantes de Llama, MiniLM, MODNet,
Mistral, Gemma, Phi ni ningún otro modelo externo dentro de este
repositorio, ni sus pesos, checkpoints o tokenizadores.

## Cobertura declarada

Este agente **no afirma cubrir la totalidad de la legislación chilena de
construcción**. Su cobertura real, en cualquier momento, es exactamente el
conjunto de documentos verificados en `documents/manifest.json` con
`es_sintetico: false` y una fuente con estado `"verificado"` en `rights/`.
Hoy ese conjunto está vacío. Cuando exista corpus real aprobado, la
cobertura debe declararse explícitamente (qué normas, qué versiones, qué
fecha de corte) y no debe generalizarse a "todo el derecho de la
construcción en Chile".

## Salvaguardas obligatorias en cada respuesta

Toda respuesta del agente (ver `schemas/response.schema.json`) incluye:
advertencia de que no sustituye asesoría profesional, recomendación de
consultar al profesional pertinente, nivel de confianza, supuestos, y
riesgos o información faltante. Si no hay evidencia documental suficiente,
la única respuesta válida es el mensaje `NO VERIFICADO` estándar — nunca
una aproximación inventada.
