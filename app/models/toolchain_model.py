"""
toolchain_model.py

Define las clases de datos que representan una cadena de herramientas (Toolchain)
y sus pasos individuales. Cada Toolchain consiste en una secuencia de ToolchainStep,
donde cada paso define qué herramienta ejecutar y cómo mapear sus entradas.
"""

from typing import List, Dict, Any

class ToolchainStep:
    """
    Representa un paso individual dentro de una Toolchain.

    Attributes:
        tool_name (str): Nombre de la herramienta a invocar.
        input_map (Dict[str, str]): Mapeo de los parámetros que necesita la herramienta.
                                     Cada clave es un parámetro del tool, y su valor es
                                     una clave del contexto acumulado (outputs anteriores).
    """
    def __init__(self, tool_name: str, input_map: Dict[str, str]):
        self.tool_name = tool_name
        self.input_map = input_map  # map: tool_param -> previous_result_field

class Toolchain:
    """
    Representa una Toolchain completa, es decir, una secuencia ordenada de pasos.

    Attributes:
        name (str): Nombre identificador de la Toolchain.
        description (str): Descripción general de la cadena de herramientas.
        steps (List[ToolchainStep]): Lista de pasos a ejecutar en orden.
    """
    def __init__(self, name: str, description: str, steps: List[ToolchainStep]):
        self.name = name
        self.description = description
        self.steps = steps
