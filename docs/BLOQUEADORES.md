# Bloqueadores explícitos antes de uso en producción

Esta lista es la condición de bloqueo real del sistema, no una lista de
tareas deseables. Mientras cualquiera de estos puntos no esté resuelto, el
agente **no debe usarse para asesorar decisiones reales** sobre
construcción, permisos, contratos o cumplimiento normativo en Chile.

## 1. Cero fuentes jurídicas verificadas y aprobadas

7 de las 8 fuentes en `sources/fuentes_aprobadas.json` fueron investigadas
el 2026-07-19 (ver [FUENTES_APROBADAS.md](FUENTES_APROBADAS.md) para el
detalle); la octava, `src-sea`, se registró recién el 2026-07-20 y todavía
no tiene ninguna investigación. Ninguna tiene los tres permisos
(`permiso_entrenamiento`, `permiso_uso_comercial`, `permiso_derivados`) en
`"si"`, así que ninguna puede usarse todavía. El resultado no es uniforme:

- **`src-poder-judicial` e `src-inn` quedaron explícitamente
  `RECHAZADO`**: hay evidencia textual de que el uso comercial y/o la
  redistribución están prohibidos bajo los términos actuales. Revertir
  esto requiere una autorización especial (Consejo Superior del Poder
  Judicial) o una licencia comercial negociada (INN) — no basta con
  "revisar mejor".
- **`src-diario-oficial`** tiene uso comercial confirmado, pero
  entrenamiento de IA y obras derivadas siguen sin evidencia.
- **`src-leychile-bcn`, `src-minvu`, `src-contraloria`** siguen
  `NO_VERIFICADO`: no se encontraron términos de uso propios (algunos
  sitios dependen de JavaScript y el fetch automatizado no pudo leerlos;
  se intentó también con Wayback Machine, sin acceso). Para MINVU y
  Contraloría se aplicó como línea base el **Art. 88 de la Ley 17.336**
  (el Estado es titular por defecto de los derechos de autor sobre obras
  de sus funcionarios), lo que llevó a fijar `permiso_entrenamiento="no"`
  de forma conservadora — no es una aprobación parcial, es lo contrario.
  Esa cita del Art. 88 se corroboró con dos fuentes secundarias
  independientes, pero no se pudo leer el texto primario de la ley
  directamente (leychile.cl no cargó vía fetch automatizado); un
  responsable humano debería confirmarla antes de usarla como base legal.
- **`src-municipalidades-dom`** ni siquiera se ha investigado (es un
  placeholder genérico sin comuna específica).
- **`src-sea`** (Servicio de Evaluación Ambiental) se registró el
  2026-07-20 para cerrar un hueco de cobertura (Ley 19.300/SEIA), pero no
  tiene ninguna investigación de derechos todavía — está en el punto de
  partida, no en `NO_VERIFICADO` post-investigación como las demás.

Ningún texto legal real puede ingerirse hasta que un responsable humano
complete la verificación pendiente, según
[RUNBOOK.md](RUNBOOK.md#flujo-para-aprobar-una-fuente-real-cuando-corresponda).

## 2. Cero documentos legales reales ingeridos

Los 7 documentos en `documents/manifest.json` son fixtures sintéticos
(`es_sintetico: true`). No hay LGUC, OGUC, circulares, dictámenes,
jurisprudencia ni normas NCh reales en este repositorio.

## 3. Motor LLM sin pesos

`agent/fixture_llm.py` no realiza inferencia real. No hay ningún modelo
local conectado. Conectar un motor real requiere: (a) autorización
independiente, (b) que el único modelo contemplado sea
`meta-llama/Llama-3.1-8B` con su procedencia preservada, y (c) que ese
motor se integre exclusivamente a través de `agent/llm_interface.py` sin
alterar las garantías de citación exclusivamente desde `retrieval/`.

## 4. Sin evaluación profesional del dominio legal

`evaluation/eval_cases/*.json` valida el comportamiento técnico del
pipeline (citación, vigencia, escalamiento, no-invención) contra fixtures
sintéticos. Ningún abogado o especialista en derecho de la construcción ha
revisado la exactitud jurídica de nada, porque todavía no hay contenido
jurídico real que revisar.

## 5. Cobertura normativa desconocida

Aun si se ingiere un primer lote de fuentes reales, la cobertura será
parcial por definición. No existe todavía un proceso para declarar y medir
qué porcentaje de la normativa relevante está efectivamente cubierto, ni
un proceso de actualización periódica ante modificaciones o derogaciones.

## 6. Sin registro de comunas/DOM específicas

`src-municipalidades-dom` es un placeholder genérico. Ninguna comuna ni
Dirección de Obras Municipales específica está registrada con su propia
URL y verificación.

## 7. Retrieval léxico sin normalización morfológica

`retrieval/search.py` no hace stemming ni lematización; ver limitación
documentada en [ARQUITECTURA.md](ARQUITECTURA.md#por-qué-tf-idf-y-no-embeddings).
Esto puede producir falsos negativos (no encontrar un artículo relevante
por diferencia de género/número) incluso con corpus real ya verificado.

## 8. Sin revisión de seguridad independiente

`security/pii_detector.py`, `security/secrets_detector.py` y
`security/prompt_injection_guard.py` son heurísticas basadas en expresiones
regulares, cubiertas por pruebas unitarias propias
(`tests/test_pii.py`, `tests/test_secrets_and_hashes.py`,
`tests/test_prompt_injection.py`) pero no han pasado por una revisión de
seguridad independiente ni por un red-team dedicado.

## 9. Falta registro de responsables

`rights/rights_manifest_example.json` incluye un campo
`responsable_verificacion` que hoy está en `NO_VERIFICADO` en todos los
casos reales. No hay todavía un proceso organizacional que asigne quién es
responsable de verificar cada fuente.
