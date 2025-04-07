import importlib.util
import os
from dynamic_tool_registry import get_all_dynamic_tools

TOOLS_FOLDER = "tools"
_loaded_tools_cache = {}
_tool_errors = []

def load_all_tools():
    global _loaded_tools_cache, _tool_errors
    _loaded_tools_cache = {}
    _tool_errors = []

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
    return _loaded_tools_cache

def get_tools():
    return {**_loaded_tools_cache, **get_all_dynamic_tools()}

def get_loading_errors():
    return _tool_errors