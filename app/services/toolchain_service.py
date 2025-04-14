"""
toolchain_service.py

Módulo encargado de ejecutar una Toolchain paso por paso, usando el contexto acumulado
como entrada y salida entre pasos.

Cada paso llama a una herramienta específica, utilizando los valores del contexto previo.
"""

from typing import Any, Dict
from app.models.toolchain_model import Toolchain
from app.core.tool_manager import call_tool_by_name

def execute_toolchain(toolchain: Toolchain, initial_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta una Toolchain paso por paso, propagando los resultados entre herramientas.

    Args:
        toolchain (Toolchain): La cadena de herramientas a ejecutar.
        initial_input (Dict[str, Any]): Contexto inicial que contiene los inputs para el primer paso.

    Returns:
        Dict[str, Any]: Contexto final después de ejecutar todos los pasos.
    """
    result_context = initial_input.copy()

    for step in toolchain.steps:
        inputs = {
            param: result_context.get(source_key, None)
            for param, source_key in step.input_map.items()
        }

        output = call_tool_by_name(step.tool_name, inputs)
        if not isinstance(output, dict):
            output = {"result": output}

        result_context.update(output)  # Merge output into context

    return result_context
