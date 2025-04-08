import importlib.util
import os
import json
from dynamic_tool_registry import get_all_dynamic_tools
from datetime import datetime

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

    # Registrar en el log de depuración
    with open("debug_logs/file_creation_debug.log", "a") as debug_file:
        debug_file.write(f"\n\n--- FUNCIÓN load_all_tools LLAMADA {datetime.now().isoformat()} ---\n")
        debug_file.write(f"Ruta de trabajo: {os.getcwd()}\n")
        debug_file.write(f"Existe TOOLS_FOLDER '{TOOLS_FOLDER}': {os.path.exists(TOOLS_FOLDER)}\n")
        
        try:
            if not os.path.exists(TOOLS_FOLDER):
                debug_file.write(f"Creando carpeta '{TOOLS_FOLDER}'...\n")
                os.makedirs(TOOLS_FOLDER)
                
            # Listar archivos en la carpeta
            files = os.listdir(TOOLS_FOLDER)
            debug_file.write(f"Archivos en '{TOOLS_FOLDER}': {files}\n")
            
            for filename in files:
                if filename.endswith(".py"):
                    module_name = filename[:-3]
                    path = os.path.join(TOOLS_FOLDER, filename)
                    
                    debug_file.write(f"Procesando archivo: {filename}, ruta: {path}\n")
                    debug_file.write(f"¿Archivo existe?: {os.path.exists(path)}\n")
                    
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, path)
                        mod = importlib.util.module_from_spec(spec)
                        debug_file.write(f"Ejecutando módulo: {module_name}...\n")
                        spec.loader.exec_module(mod)
                        
                        debug_file.write(f"Atributos del módulo: {dir(mod)}\n")
                        debug_file.write(f"¿Tiene schema?: {hasattr(mod, 'schema')}\n")
                        debug_file.write(f"¿Tiene función llamable?: {callable(getattr(mod, module_name, None))}\n")

                        if hasattr(mod, "schema") and callable(getattr(mod, module_name, None)):
                            _loaded_tools_cache[mod.schema["name"]] = {
                                "schema": mod.schema,
                                "func": getattr(mod, module_name)
                            }
                            debug_file.write(f"Herramienta '{mod.schema['name']}' cargada correctamente\n")
                        else:
                            error_msg = "Falta 'schema' o función no encontrada"
                            debug_file.write(f"ERROR: {error_msg}\n")
                            raise Exception(error_msg)
                    except Exception as e:
                        debug_file.write(f"ERROR al cargar {filename}: {str(e)}\n")
                        import traceback
                        debug_file.write(f"TRACEBACK: {traceback.format_exc()}\n")
                        _tool_errors.append({"file": filename, "error": str(e)})
                        
            debug_file.write(f"Herramientas cargadas: {list(_loaded_tools_cache.keys())}\n")
            
        except Exception as general_e:
            debug_file.write(f"ERROR GENERAL: {str(general_e)}\n")
            import traceback
            debug_file.write(f"TRACEBACK GENERAL: {traceback.format_exc()}\n")

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