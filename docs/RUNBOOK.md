# Runbook — comandos reproducibles

Todos los comandos se ejecutan desde la raíz de este repositorio
(`Amalan-Agente-Construccion-Chile/`), con Python 3.10+ y sin dependencias
externas (solo librería estándar).

## Consultar al agente

```bash
python -m app.cli "Cual es el plazo simulado de tramitacion del permiso ficticio"
python -m app.cli --json "Que exige la accesibilidad universal"
python -m app.cli --tipo-norma jurisprudencia "Que dice la sentencia ficticia sobre contrato de construccion"
python -m app.cli --materia "accesibilidad" --json "Que exige"
```

Salida humana por defecto; `--json` para la respuesta estructurada completa
según `schemas/response.schema.json`.

## Verificar integridad documental (hashes)

```bash
python scripts/verify_manifest.py
```

Código de salida `0` si todos los hashes de `documents/manifest.json`
coinciden con el contenido real de `documents/synthetic/`; `1` si hay algún
desajuste.

## Revisar qué fuentes están bloqueadas para ingesta

```bash
python scripts/ingest_approved_sources.py
```

En el estado actual del repositorio, debe reportar las 8 fuentes de
`sources/fuentes_aprobadas.json` como `BLOQUEADA` (ninguna tiene derechos
verificados todavía). Si alguna vez reporta una fuente `APROBADA`, verificar
que exista evidencia real en `rights/` antes de confiar en ese resultado.

## Correr el harness de evaluación

```bash
python evaluation/run_eval.py
```

Ejecuta todos los casos en `evaluation/eval_cases/*.json` contra el
orquestador real y compara expectativas declaradas. Código `0` si todos los
casos pasan.

## Ver el avance de la cobertura objetivo del dominio

```bash
python scripts/coverage_report.py
```

Resume `sources/cobertura_objetivo.json` (normas/áreas específicas que
definen el alcance completo del dominio, no solo las 8 fuentes
institucionales) y falla si algún objetivo está marcado `aprobada` sin un
manifiesto de derechos real que lo respalde.

## Agregar un documento verificado al manifiesto (ingesta real)

```bash
python scripts/add_verified_document.py <ruta_al_documento.json> --dry-run
python scripts/add_verified_document.py <ruta_al_documento.json>
```

El documento debe estar ya ubicado en su ruta final dentro del
repositorio y tener los campos requeridos por
`schemas/document_manifest.schema.json`. La herramienta **rechaza la
ingesta automáticamente** si `source_id` no tiene un manifiesto de
derechos aprobado en `rights/` (los tres permisos en `"si"` y
`estado_verificacion="verificado"`) — no hace falta acordarse de correr
`ingest_approved_sources.py` por separado, el gate está embebido. Usar
`--dry-run` para ver qué se agregaría sin escribir nada. Con el estado
actual del repositorio (ninguna fuente aprobada), cualquier invocación
real debe fallar con código de salida `1`.

## Correr la suite de pruebas

```bash
python -m unittest discover -s tests -v
```

## Auditoría completa (todo lo anterior en un solo comando)

```bash
python scripts/run_audit.py
```

Verifica estructura de carpetas, hashes, estado de ingesta de fuentes y
evaluación; imprime un resumen. Complementa, pero no reemplaza,
[INFORME_AUDITORIA_INICIAL.md](INFORME_AUDITORIA_INICIAL.md).

## Ver el registro de auditoría de respuestas reales

```bash
python -c "import json,pathlib; [print(json.loads(l)) for l in pathlib.Path('provenance/audit_log.jsonl').read_text(encoding='utf-8').splitlines()]"
```

(El archivo no existe hasta la primera vez que se llama a
`agent.orchestrator.Orchestrator.answer` fuera del harness de evaluación,
que usa su propio log en `evaluation/results/eval_audit_log.jsonl` para no
mezclar corridas de prueba con uso real.)

## Flujo para aprobar una fuente real (cuando corresponda)

1. Revisar términos de uso reales de la institución.
2. Completar un manifiesto en `rights/` según
   `schemas/rights.schema.json` (usar `rights/rights_manifest_example.json`
   como plantilla) con evidencia concreta.
3. Actualizar la entrada correspondiente en
   `sources/fuentes_aprobadas.json`.
4. Volver a correr `python scripts/ingest_approved_sources.py` — la fuente
   debe pasar de `BLOQUEADA` a `APROBADA` solo si los tres permisos están
   en `"si"` y el estado de verificación es `"verificado"`.
5. Solo entonces agregar el documento real a `documents/manifest.json` con
   `es_sintetico: false`, su hash SHA-256 real, y volver a correr
   `scripts/verify_manifest.py`.
