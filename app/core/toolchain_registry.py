'''
Este archivo es el encargado de registrar las toolchains en memoria.

La lógica de este archivo es la siguiente:

1. Carga todas las toolchains desde el archivo toolchains.json
2. Registra cada toolchain en memoria
'''

import os
import json
from datetime import datetime
from typing import Dict
from app.models.toolchain_model import Toolchain, ToolchainStep

# Definir rutas
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
CONFIG_DIR = os.path.join(APP_DIR, "config")
TOOLCHAINS_FILE = os.path.join(CONFIG_DIR, "toolchains.json")

# Asegurar que el directorio config existe
os.makedirs(CONFIG_DIR, exist_ok=True)

# Registro dinámico en memoria
_toolchain_registry: Dict[str, Toolchain] = {}

def register_toolchain(toolchain: Toolchain) -> str:
    """
    Registra una toolchain en memoria y devuelve su nombre.

    Args:
        toolchain (Toolchain): Objeto toolchain a registrar.

    Returns:
        str: Nombre de la toolchain registrada.
    """
    _toolchain_registry[toolchain.name] = toolchain
    return toolchain.name

def get_all_toolchains() -> Dict[str, Toolchain]:
    """
    Devuelve todas las toolchains registradas en memoria.

    Returns:
        Dict[str, Toolchain]: Diccionario de toolchains por nombre.
    """
    return _toolchain_registry

def get_toolchain(name: str) -> Toolchain:
    """
    Devuelve una toolchain específica por nombre.

    Args:
        name (str): Nombre de la toolchain.

    Returns:
        Toolchain: Objeto toolchain o None si no existe.
    """
    return _toolchain_registry.get(name)

def delete_toolchain(name: str) -> bool:
    """
    Elimina una toolchain del registro en memoria.

    Args:
        name (str): Nombre de la toolchain.

    Returns:
        bool: True si se eliminó, False si no existía.
    """
    if name in _toolchain_registry:
        del _toolchain_registry[name]
        return True
    return False

def save_toolchains_to_disk(path=TOOLCHAINS_FILE) -> bool:
    """
    Guarda todas las toolchains registradas en un archivo JSON.

    Args:
        path (str): Ruta al archivo.

    Returns:
        bool: True si la operación fue exitosa.
    """
    try:
        data = []
        for t in _toolchain_registry.values():
            data.append({
                "name": t.name,
                "description": t.description,
                "steps": [
                    {"tool_name": s.tool_name, "input_map": s.input_map}
                    for s in t.steps
                ]
            })

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar toolchains: {e}")
        return False

def load_toolchains_from_disk(path=TOOLCHAINS_FILE) -> Dict[str, Toolchain]:
    """
    Carga toolchains desde el disco al registro en memoria.

    Args:
        path (str): Ruta al archivo.

    Returns:
        Dict[str, Toolchain]: Toolchains cargadas.
    """
    global _toolchain_registry
    _toolchain_registry = {}  # Limpiar antes de cargar
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for chain in data:
                steps = [ToolchainStep(**step) for step in chain["steps"]]
                tc = Toolchain(chain["name"], chain["description"], steps)
                _toolchain_registry[tc.name] = tc
    except FileNotFoundError:
        pass  # No hay archivo aún
    except Exception as e:
        print(f"[ERROR] Error al cargar toolchains: {e}")
    return _toolchain_registry