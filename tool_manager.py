import importlib.util
import os
import json
from dynamic_tool_registry import get_all_dynamic_tools

TOOLS_FOLDER = "tools"
TOOL_STATUS_FILE = ".tool_status.json"
_loaded_tools_cache = {}
_tool_errors = []
_tool_status = {}

def _load_tool_status():
    global _tool_status
    try:
        if os.path.exists(TOOL_STATUS_FILE):
            with open(TOOL_STATUS_FILE, 'r') as f:
                _tool_status = json.load(f)
        else:
            _tool_status = {}
    except Exception:
        _tool_status = {}

def _save_tool_status():
    with open(TOOL_STATUS_FILE, 'w') as f:
        json.dump(_tool_status, f, indent=2)

def set_tool_status(tool_name: str, active: bool):
    """Activa o desactiva una herramienta específica"""
    _tool_status[tool_name] = active
    _save_tool_status()

def is_tool_active(tool_name: str) -> bool:
    """Verifica si una herramienta está activa"""
    return _tool_status.get(tool_name, True)  # Por defecto, las herramientas están activas

def load_all_tools():
    global _loaded_tools_cache, _tool_errors
    _loaded_tools_cache = {}
    _tool_errors = []
    _load_tool_status()  # Cargamos el estado de las herramientas

    if not os.path.exists(TOOLS_FOLDER):
        os.makedirs(TOOLS_FOLDER)

    for filename in os.listdir(TOOLS_FOLDER):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            path = os.path.join(TOOLS_FOLDER, filename)
            try:
                spec = importlib.util.spec_from_file_location(module_name, path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                if hasattr(mod, "schema") and callable(getattr(mod, module_name, None)):
                    _loaded_tools_cache[mod.schema["name"]] = {
                        "schema": mod.schema,
                        "func": getattr(mod, module_name)
                    }
                else:
                    raise Exception("Falta 'schema' o función no encontrada")
            except Exception as e:
                _tool_errors.append({"file": filename, "error": str(e)})

    return _loaded_tools_cache

def get_all_loaded_tools():
    """Devuelve todas las herramientas cargadas, incluyendo las inactivas"""
    return _loaded_tools_cache

def get_tools():
    """Devuelve solo las herramientas activas"""
    all_tools = {**_loaded_tools_cache, **get_all_dynamic_tools()}
    return {name: tool for name, tool in all_tools.items() if is_tool_active(name)}

def get_loading_errors():
    return _tool_errors

def get_tool_status():
    """Devuelve el estado de todas las herramientas"""
    return _tool_status