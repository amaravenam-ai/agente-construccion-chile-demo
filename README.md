# Agente de Construcción Chile — demostración sintética

Prototipo de Ariel Aravena para practicar recuperación documental, citas trazables, control de vigencia y pruebas de seguridad. Preparado con asistencia de Codex.

**Solo documentos ficticios. No proporciona asesoría jurídica validada ni contiene leyes reales.** El adaptador responde con fixtures; no usa pesos de un modelo ni un proveedor externo.

## Requisitos y ejecución

Python 3.12, sin paquetes externos. Desde la raíz:

```sh
python -m app.cli --json "Cual es el plazo simulado de tramitacion del permiso ficticio"
python -m unittest discover -s tests -q
python scripts/run_audit.py
```

## Flujo

Pregunta → filtro de entrada → recuperación léxica → control documental → citas → respuesta estructurada → auditoría local.

Las ocho fuentes jurídicas candidatas están bloqueadas. Incluirlas en el registro no concede derechos ni las ingiere. Los fixtures llevan marcadores explícitos y hashes que verifica `scripts/verify_manifest.py`.

## Verificado en la preparación

72 pruebas unitarias y 6 casos del evaluador aprobados. Integridad de fixtures correcta; cero fuentes reales aprobadas. Se corrigió el código de salida del comando de auditoría para que un fallo del evaluador no se oculte.
El ejemplo devuelve dos versiones ficticias citadas y distingue su estado. Ver `evidencia/resumen.json` y `docs/RUNBOOK.md`.

## Alcance y derechos

El trabajo demuestra controles de software y recuperación léxica; no conocimiento jurídico ni entrenamiento de un LLM. Los logs nuevos son locales y no deben subirse. Autoría propia declarada por su titular; la preparación de portafolio incluye revisión y asistencia de Codex. Ver `AVISO_DERECHOS.md` y `TERCEROS.md`.
