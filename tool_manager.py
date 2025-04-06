import importlib.util
import os
from typing import Dict
from dynamic_tool_registry import get_all_dynamic_tools

TOOLS_FOLDER = "tools"
_loaded_tools_cache = {}
_tool_errors = []

def load_all_tools() -> Dict[str, Dict]:
    global _loaded_tools_cache, _tool_errors
    _loaded_tools_cache = {}
    _tool_errors = []

    for filename in os.listdir(TOOLS_FOLDER):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            path = os.path.join(TOOLS_FOLDER, filename)
            try:
                spec = importlib.util.spec_from_file_location(module_name, path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                # Verificamos si hay 'schema' y la función con el mismo nombre que el archivo
                if hasattr(mod, "schema") and callable(getattr(mod, module_name, None)):
                    _loaded_tools_cache[mod.schema["name"]] = {
                        "schema": mod.schema,
                        "func": getattr(mod, module_name)
                    }
                else:
                    raise Exception("Falta 'schema' o la función principal no coincide con el nombre del archivo")
            except Exception as e:
                _tool_errors.append({"file": filename, "error": str(e)})

    return _loaded_tools_cache

def get_all_loaded_tools():
    return _loaded_tools_cache

def get_loading_errors():
    return _tool_errors

def get_tools_for_user_object(user_obj):
    # user_obj puede ser un dict con "tools" o un string "anon"
    if isinstance(user_obj, dict) and "tools" in user_obj:
        allowed = user_obj["tools"]
    else:
        # Modo simplificado: permitimos TODAS las tools
        allowed = list(get_all_loaded_tools().keys()) + list(get_all_dynamic_tools().keys())

    all_tools = {**get_all_loaded_tools(), **get_all_dynamic_tools()}
    return {name: info for name, info in all_tools.items() if name in allowed}
