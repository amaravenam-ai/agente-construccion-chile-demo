"""CLI reproducible para consultar el agente desde línea de comandos.

Uso (ejecutar desde la raíz del repositorio):
    python -m app.cli "¿Qué plazo tiene la recepción de una obra?"
    python -m app.cli --materia "accesibilidad" "¿Qué exige la accesibilidad universal?"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent.orchestrator import Orchestrator  # noqa: E402
from retrieval.search import SearchFilters  # noqa: E402


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Consulta al Amalan Agente de Construcción Chile (fase de fixtures sintéticos).")
    parser.add_argument("pregunta", type=str, help="Pregunta en lenguaje natural.")
    parser.add_argument("--materia", type=str, default=None)
    parser.add_argument("--organismo", type=str, default=None)
    parser.add_argument("--tipo-norma", type=str, default=None, dest="tipo_norma")
    parser.add_argument("--estado-vigencia", type=str, default=None, dest="estado_vigencia")
    parser.add_argument("--region", type=str, default=None)
    parser.add_argument("--comuna", type=str, default=None)
    parser.add_argument("--json", action="store_true", help="Imprimir la respuesta como JSON.")
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    filters = SearchFilters(
        materia=args.materia,
        organismo=args.organismo,
        tipo_norma=args.tipo_norma,
        estado_vigencia=args.estado_vigencia,
        region=args.region,
        comuna=args.comuna,
    )

    orchestrator = Orchestrator()
    response = orchestrator.answer(args.pregunta, filters=filters)

    if args.json:
        print(json.dumps(response.to_dict(), ensure_ascii=False, indent=2))
    else:
        _print_human(response)
    return 0


def _print_human(response) -> None:
    print(f"Resumen: {response.resumen}")
    print(f"Jurisdicción: {response.jurisdiccion}")
    print(f"Fecha de consulta: {response.fecha_consulta}")
    print(f"Norma o documento: {', '.join(response.norma_o_documento) or '(ninguno)'}")
    print(f"Artículo/sección/página: {', '.join(response.articulo_seccion_pagina) or '(ninguno)'}")
    print(f"Vigencia conocida: {response.vigencia_conocida}")
    print(f"Nivel de confianza: {response.nivel_confianza}")
    print(f"Supuestos: {', '.join(response.supuestos) or '(ninguno)'}")
    print(f"Riesgos / información faltante: {', '.join(response.riesgos_informacion_faltante) or '(ninguno)'}")
    print(f"Advertencia: {response.advertencia}")
    print(f"Recomendación: {response.recomendacion}")
    print(f"NO VERIFICADO: {response.no_verificado}")
    print(f"Escalamiento requerido: {response.escalamiento_requerido}")
    print(f"ID de auditoría: {response.auditoria_id}")


if __name__ == "__main__":
    raise SystemExit(main())
