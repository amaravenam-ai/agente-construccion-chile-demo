# Fuentes jurídicas — estado de aprobación

Fuente de verdad operativa: `sources/fuentes_aprobadas.json` (validado por
`schemas/source_registry.schema.json`). Esta tabla es un resumen legible;
ante cualquier discrepancia, el JSON manda.

**Ninguna fuente está aprobada para ingesta real todavía.** Ejecutar
`python scripts/ingest_approved_sources.py` para ver el bloqueo recalculado
en cualquier momento. Los 6 registros de `rights/` con investigación real
(uno por fuente investigada, más `rights_manifest_example.json` como
plantilla) contienen el detalle completo de cada investigación —
`src-sea` es la única de las 8 fuentes registradas que todavía no tiene
un manifiesto de derechos propio, ver más abajo.

## Fuente institucional vs. norma específica

Este documento y `sources/fuentes_aprobadas.json` registran **fuentes
institucionales** (8 portales: BCN, Diario Oficial, MINVU, Contraloría,
Poder Judicial, INN, Municipalidades/DOM genérico, y SEA). Eso es
necesario pero no suficiente para "todo respecto a construcción": una
institución como MINVU publica cientos de circulares y reglamentos
distintos, cada uno con su propia vigencia y eventualmente sus propios
derechos.

Por eso existe **`sources/cobertura_objetivo.json`** (validado por
`schemas/cobertura_objetivo.schema.json`): una lista de **normas y áreas
específicas** dentro de esas instituciones — LGUC, OGUC, circulares DDU,
Ley 20.123 de subcontratación, Ley 16.744, DS 594, Ley 19.300/SEIA, Ley
21.442 de copropiedad, Ley 21.305 de eficiencia energética, catálogo NCh,
dictámenes y jurisprudencia relacionados con construcción, entre otras —
que define el alcance completo que el agente debería cubrir eventualmente.
Ejecutar `python scripts/coverage_report.py` para ver el avance.

Cada objetivo en `cobertura_objetivo.json` **hereda** el estado de la
investigación institucional ya realizada cuando esa investigación aplica
completa y directamente (p. ej. el rechazo de INN cubre todas las normas
NCh sin excepción). Ningún objetivo nuevo tiene contenido, vigencia ni
artículos verificados — son huecos por llenar, no fuentes aprobadas.
Dos huecos de registro identificados al construir esta lista: (1) **YA
RESUELTO 2026-07-20**: se registró `src-sea` (Servicio de Evaluación
Ambiental) como fuente institucional para el objetivo de Ley 19.300/SEIA
— sigue pendiente investigar sus derechos, solo se cerró el hueco de
registro; (2) sigue sin decidirse qué comunas priorizar para
Municipalidades/DOM.

## Estado por fuente (investigación real realizada el 2026-07-19, salvo `src-sea` registrada el 2026-07-20)

| id | Institución | Materia | Resultado de la investigación |
|---|---|---|---|
| `src-leychile-bcn` | BCN (Ley Chile) | LGUC, legislación general | NO_VERIFICADO — señal positiva parcial, sin confirmar para el texto legal completo |
| `src-diario-oficial` | Diario Oficial | Publicaciones y modificaciones normativas | NO_VERIFICADO — uso comercial confirmado explícitamente; entrenamiento IA y derivados sin confirmar |
| `src-poder-judicial` | Poder Judicial | Jurisprudencia | **RECHAZADO** — uso comercial y derivados explícitamente prohibidos sin autorización especial |
| `src-inn` | INN | Normas NCh | **RECHAZADO** — reproducción/redistribución explícitamente prohibida sin licencia comercial |
| `src-minvu` | MINVU | OGUC, circulares DDU | NO_VERIFICADO — sin términos propios; entrenamiento IA en "no" por regla general (Art. 88) |
| `src-sea` | Servicio de Evaluación Ambiental | Evaluación de impacto ambiental (SEIA) | **NO INVESTIGADA TODAVÍA** — solo registrada como puntero institucional, sin manifiesto en `rights/` |
| `src-contraloria` | Contraloría | Dictámenes | NO_VERIFICADO — sin términos propios; entrenamiento IA en "no" por regla general (Art. 88) |
| `src-municipalidades-dom` | Municipalidades y DOM (genérico) | Ordenanzas locales | NO_VERIFICADO — placeholder, ninguna comuna registrada todavía, no investigado |

`NO_VERIFICADO` significa "no hay evidencia suficiente ni a favor ni en
contra". `RECHAZADO` significa "hay evidencia explícita de que el uso
previsto está prohibido bajo los términos actuales" — es un resultado más
fuerte y más útil que `NO_VERIFICADO`, porque evita reinvestigar algo ya
resuelto y dice exactamente qué autorización adicional se necesitaría.

## Hallazgo general aplicable a todas las fuentes estatales: Artículo 88, Ley 17.336

Durante la investigación se ubicó y corroboró (con dos fuentes secundarias
independientes) el **Artículo 88 de la Ley 17.336** (Propiedad
Intelectual): el Estado, los municipios, las corporaciones oficiales y las
instituciones semifiscales o autónomas son **titulares del derecho de
autor** sobre las obras producidas por sus funcionarios en el desempeño de
sus cargos. En otras palabras: **por defecto, el texto de leyes, OGUC,
circulares, dictámenes, etc. no es de dominio público automático** — es
propiedad del organismo que lo produjo, salvo que ese organismo lo libere
explícitamente (como parece hacer Diario Oficial con sus condiciones de
reutilización publicadas, y posiblemente BCN con su catálogo de datos
abiertos).

**Advertencia de confiabilidad**: no se pudo leer el texto primario de la
Ley 17.336 directamente (leychile.cl no cargó vía fetch automatizado por
ser una página dinámica); el Artículo 88 se corroboró vía dos fuentes
secundarias que citan el texto de forma coincidente, pero esto sigue sin
ser una lectura directa del BOE/Diario Oficial ni de leychile.cl. Un
responsable humano debería confirmar esta cita antes de tomarla como base
de una decisión legal.

**Consecuencia práctica aplicada en esta investigación**: para MINVU y
Contraloría, donde no se encontró ninguna liberación explícita propia, se
fijó `permiso_entrenamiento = "no"` como interpretación conservadora del
silencio bajo este artículo (evita asumir un "sí" sin evidencia).
`permiso_uso_comercial` y `permiso_derivados` se dejaron `NO_VERIFICADO`
en vez de también "no", porque decidir eso con la misma confianza
requeriría revisar si aplican otras excepciones de la ley (cita, uso
educativo) — eso excede lo que una búsqueda automatizada puede concluir
con seguridad.

## Qué falta para cada fuente

Por cada fuente, un responsable humano debe:

1. Leer los términos de uso/licencia publicados por la institución (o
   revisar/confirmar los ya encontrados en `rights/`).
2. Registrar en `rights/` (según `schemas/rights.schema.json`) evidencia
   concreta: texto de la licencia, enlace archivado, o autorización
   explícita recibida.
3. Fijar `permiso_entrenamiento`, `permiso_uso_comercial` y
   `permiso_derivados` en `"si"` o `"no"` según corresponda — nunca dejar
   `NO_VERIFICADO` una vez revisado.
4. Cambiar `estado_verificacion` a `"verificado"` o `"rechazado"`.
5. Solo si los tres permisos quedan en `"si"` y el estado es
   `"verificado"`, la fuente queda habilitada para que un documento suyo
   pueda registrarse en `documents/manifest.json` con `es_sintetico: false`.

## Detalle de la investigación por fuente

### `src-leychile-bcn` — Ley Chile / BCN

El catálogo de datos abiertos de BCN (`datos.bcn.cl`) declara reutilización
"sin restricciones de copyright", pero no se confirmó que ese régimen
cubra el texto legal completo de `leychile.cl` (distinto de sus metadatos
estructurados), ni uso comercial, ni entrenamiento de IA. Tampoco se pudo
ubicar el artículo de la Ley 17.336 que declare los textos oficiales del
Estado como dominio público (se intentó vía BCN, WIPO Lex, PDF oficial y
Wikipedia). **Siguiente paso**: contacto directo con BCN, o lectura manual
humana del texto completo de la Ley 17.336. Detalle:
`rights/rights_manifest_src-leychile-bcn.json`.

### `src-diario-oficial` — Diario Oficial

Sus condiciones de uso (`/condiciones/`) declaran explícitamente que la
reutilización "está abierta a todos, incluso para aquienes ya exploten
legítimamente productos con valor añadido", sin otorgar exclusividad a
nadie — evidencia razonablemente clara de permiso de uso comercial. Exige
no alterar el contenido, no desnaturalizar el sentido, y citar fuente y
fecha. No menciona entrenamiento de IA ni obras derivadas transformativas
(como resúmenes generados por IA), por lo que esos dos permisos quedan
`NO_VERIFICADO`. Detalle: `rights/rights_manifest_src-diario-oficial.json`.

### `src-poder-judicial` — Poder Judicial (RECHAZADO)

Sus condiciones de uso (`/post/condiciones-de-uso-de-este-portal`)
autorizan el uso únicamente para "fines particulares o académicos" —
excluye explícitamente uso comercial — y prohíben el "tratamiento masivo
de datos y contenidos" sin autorización previa del Consejo Superior, lo
que aplicaría directamente a cualquier ingesta tipo RAG. Para revertir
este rechazo se requeriría solicitar esa autorización especial. Detalle:
`rights/rights_manifest_src-poder-judicial.json`.

### `src-inn` — INN / normas NCh (RECHAZADO)

Confirmado: las normas NCh/NCh-ISO se venden individualmente y su
reproducción o redistribución está prohibida sin permiso escrito del
propietario; reventa y uso compartido de archivos están expresamente
prohibidos. No ingerir ningún contenido salvo que se negocie una licencia
comercial explícita con INN que cubra su uso en un sistema de
recuperación/IA. Detalle: `rights/rights_manifest_src-inn.json`.

### `src-minvu` — MINVU

No se encontró ninguna página de términos de uso, aviso legal ni licencia
de reutilización propia (se intentó también `site:minvu.gob.cl` y Wayback
Machine, sin éxito); el sitio solo expone política de privacidad y
transparencia activa en su footer. `permiso_entrenamiento` se fijó en
`"no"` aplicando el Art. 88 (ver arriba) como línea base conservadora.
**Siguiente paso**: contacto directo con MINVU (Minvu Aló, 600 901 11 11)
o revisión manual humana. Detalle: `rights/rights_manifest_src-minvu.json`.

### `src-contraloria` — Contraloría

El sitio depende fuertemente de JavaScript; el fetch automatizado no pudo
leer contenido útil de la página principal, y las búsquedas web (incluida
`site:contraloria.cl` y Wayback Machine) tampoco ubicaron una página de
términos específica. `permiso_entrenamiento` se fijó en `"no"` aplicando
el Art. 88 como línea base conservadora. **Corrección importante**: los
dictámenes de Contraloría SÍ son vinculantes para la Administración del
Estado (jurisprudencia administrativa de efecto general) — a diferencia
de la jurisprudencia judicial, que no es vinculante. Una nota anterior de
este documento lo describía erróneamente; ya se corrigió. **Siguiente
paso**: revisión manual humana con navegador real, o contacto directo con
la institución. Detalle: `rights/rights_manifest_src-contraloria.json`.

### `src-municipalidades-dom` — Municipalidades y DOM

Placeholder genérico, no investigado: cada comuna es una fuente distinta
con su propia URL y verificación; no existe un registro único válido para
todas las comunas de Chile.

### `src-sea` — Servicio de Evaluación Ambiental

Registrada el 2026-07-20 para cerrar un hueco de registro identificado al
construir `sources/cobertura_objetivo.json`: el organismo administrador
del Sistema de Evaluación de Impacto Ambiental (SEIA) no tenía ninguna
fuente institucional propia, a pesar de que "medio ambiente y evaluación
de proyectos" es uno de los bloques temáticos del alcance original del
agente. **Aún no se ha investigado ningún término de uso ni derecho de
esta fuente** — está exactamente en el mismo punto de partida que las
otras 7 fuentes estaban antes de la investigación del 2026-07-19: solo un
puntero institucional (`https://www.sea.gob.cl`), sin manifiesto en
`rights/`. No tiene un archivo `rights/rights_manifest_src-sea.json`
todavía; `scripts/ingest_approved_sources.py` la bloquea automáticamente
por la misma razón que bloquearía cualquier fuente sin manifiesto (ver
`scripts/ingest_approved_sources.py:_rights_manifest_for_source`, que cae
al fallback conservador cuando no existe el archivo dedicado).
