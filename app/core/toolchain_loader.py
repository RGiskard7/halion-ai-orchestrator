"""
toolchain_loader.py

Carga toolchains definidas como JSON desde un archivo, transformándolas en instancias
de la clase Toolchain para su ejecución o visualización.
"""

import os
import json
from app.models.toolchain_model import Toolchain, ToolchainStep

# Definir rutas absolutas basadas en la ubicación actual del script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)    # Directorio app/
ROOT_DIR = os.path.dirname(APP_DIR)       # Directorio raíz del proyecto
CONFIG_DIR = os.path.join(APP_DIR, "config") # Directorio app/config/

# Asegurar que el directorio config existe
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR, exist_ok=True)

TOOLCHAINS_FILE = os.path.join(CONFIG_DIR, "toolchains.json")

def load_toolchains_from_file(path=TOOLCHAINS_FILE):
    """
    Carga todas las Toolchains definidas en un archivo JSON.

    Args:
        path (str): Ruta al archivo JSON que contiene la definición de las toolchains.

    Returns:
        List[Toolchain]: Lista de objetos Toolchain listos para ser usados.
    """
    with open(path, "r") as f:
        raw_data = json.load(f)

    toolchains = []
    for chain in raw_data:
        # Convertir cada paso en una instancia de ToolchainStep
        steps = [ToolchainStep(**step) for step in chain["steps"]]

        # Crear la Toolchain final
        toolchains.append(Toolchain(
            name=chain["name"],
            description=chain["description"],
            steps=steps
        ))
    return toolchains
