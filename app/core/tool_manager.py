'''
Este archivo es el orquestador central de herramientas. Gestiona tanto las tools estáticas como las dinámicas, 
usando funciones utilitarias. Está perfecto en core, porque es una lógica de bajo nivel transversal al sistema.

La lógica de la tool manager es la siguiente:

1. Carga el estado de las herramientas desde el archivo .tool_status.json
2. Carga todas las herramientas estáticas y dinámicas
3. Devuelve las herramientas activas
'''

import importlib.util
import os
import json
from app.core.tool_definition_registry import get_all_dynamic_tools, TOOLS_FOLDER, DEBUG_LOGS_FOLDER
from datetime import datetime

# Definir rutas absolutas basadas en la ubicación actual del script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)       # Directorio app/
ROOT_DIR = os.path.dirname(APP_DIR)          # Directorio raíz del proyecto
CONFIG_DIR = os.path.join(APP_DIR, "config") # Directorio app/config/

# Asegurar que el directorio config existe
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR, exist_ok=True)

TOOL_STATUS_FILE = os.path.join(CONFIG_DIR, ".tool_status.json")

# Asegurarse de que existan los directorios necesarios
os.makedirs(TOOLS_FOLDER, exist_ok=True)
os.makedirs(DEBUG_LOGS_FOLDER, exist_ok=True)

_loaded_tools_cache = {}
_tool_errors = []
_tool_status = {}

def _load_tool_status():
    global _tool_status
    try:
        if os.path.exists(TOOL_STATUS_FILE):
            with open(TOOL_STATUS_FILE, 'r') as f:
                loaded_data = json.load(f)
                # Adaptar al nuevo formato: {"tool_name": {"active": bool, "postprocess": bool}}
                # Mantener compatibilidad con el formato antiguo: {"tool_name": bool}
                _tool_status = {}
                for name, status in loaded_data.items():
                    if isinstance(status, dict):
                        _tool_status[name] = {
                            "active": status.get("active", True), # Default active a True si falta
                            "postprocess": status.get("postprocess", True) # Default postprocess a True si falta
                        }
                    elif isinstance(status, bool): # Formato antiguo
                        _tool_status[name] = {
                            "active": status,
                            "postprocess": True # Asumir postprocess True para formato antiguo
                        }
        else:
            _tool_status = {} # Si el archivo no existe, empezar vacío
    except (json.JSONDecodeError, IOError) as e:
        print(f"[ERROR] No se pudo cargar o parsear {TOOL_STATUS_FILE}: {e}")
        _tool_status = {}

def _save_tool_status():
    try:
        with open(TOOL_STATUS_FILE, 'w') as f:
            json.dump(_tool_status, f, indent=2)
    except IOError as e:
        print(f"[ERROR] No se pudo guardar {TOOL_STATUS_FILE}: {e}")

def set_tool_status(tool_name: str, active: bool):
    """Activa o desactiva una herramienta específica"""
    if tool_name not in _tool_status: # Inicializar si no existe
        _tool_status[tool_name] = {"active": True, "postprocess": True}
    _tool_status[tool_name]["active"] = active
    _save_tool_status()

def is_tool_active(tool_name: str) -> bool:
    """Verifica si una herramienta está activa"""
    # Devuelve el valor 'active', default a True si la tool no está en el registro
    return _tool_status.get(tool_name, {}).get("active", True)

def set_tool_postprocess(tool_name: str, postprocess_active: bool):
    """Activa o desactiva el postprocesado para una herramienta específica"""
    if tool_name not in _tool_status: # Inicializar si no existe
        _tool_status[tool_name] = {"active": True, "postprocess": True}
    _tool_status[tool_name]["postprocess"] = postprocess_active
    _save_tool_status()

def get_tool_postprocess(tool_name: str) -> bool:
    """Verifica si el postprocesado está activo para una herramienta"""
    # Devuelve el valor 'postprocess', default a True si la tool no está en el registro
    return _tool_status.get(tool_name, {}).get("postprocess", True)

def load_all_tools():
    global _loaded_tools_cache, _tool_errors
    _loaded_tools_cache = {}
    _tool_errors = []
    _load_tool_status()  # Cargamos el estado de las herramientas

    # Asegurar que exista el directorio de logs
    os.makedirs(DEBUG_LOGS_FOLDER, exist_ok=True)
    debug_log_path = os.path.join(DEBUG_LOGS_FOLDER, "file_creation_debug.log")

    # Registrar en el log de depuración
    with open(debug_log_path, "a") as debug_file:
        debug_file.write(f"\n\n--- FUNCIÓN load_all_tools LLAMADA {datetime.now().isoformat()} ---\n")
        debug_file.write(f"Ruta de trabajo: {os.getcwd()}\n")
        debug_file.write(f"Existe TOOLS_FOLDER '{TOOLS_FOLDER}': {os.path.exists(TOOLS_FOLDER)}\n")
        
        try:
            if not os.path.exists(TOOLS_FOLDER):
                debug_file.write(f"Creando carpeta '{TOOLS_FOLDER}'...\n")
                os.makedirs(TOOLS_FOLDER, exist_ok=True)
                
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
                        # No ejecutar el módulo aquí directamente si no es necesario
                        spec.loader.exec_module(mod)
                        
                        debug_file.write(f"Atributos del módulo: {dir(mod)}\n")
                        debug_file.write(f"¿Tiene schema?: {hasattr(mod, 'schema')}\n")
                        debug_file.write(f"¿Tiene función llamable?: {callable(getattr(mod, module_name, None))}\n")

                        if hasattr(mod, "schema") and callable(getattr(mod, module_name, None)):
                            # Guardar el schema original y añadir el estado de postprocess
                            _loaded_tools_cache[mod.schema["name"]] = {
                                "schema": mod.schema, # Schema original del archivo
                                "func": getattr(mod, module_name)
                            }
                            # El estado 'active' y 'postprocess' se consultan via is_tool_active/get_tool_postprocess
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
    active_tools = {}
    for name, tool in all_tools.items():
        if is_tool_active(name):
            # Devolver una copia del schema con el estado de postprocess actual
            # para que la API de OpenAI lo reciba correctamente si es necesario.
            current_schema = tool.get("schema", {}).copy()
            current_schema["postprocess"] = get_tool_postprocess(name)
            active_tools[name] = {
                "schema": current_schema,
                "func": tool.get("func")
            }
    return active_tools

def get_loading_errors():
    return _tool_errors

def get_tool_status():
    """Devuelve el estado de todas las herramientas"""
    return _tool_status

def call_tool_by_name(tool_name: str, arguments: dict):
    """
    Ejecuta una herramienta por su nombre, pasando los argumentos proporcionados.

    Args:
        tool_name (str): Nombre de la herramienta.
        arguments (dict): Diccionario con los argumentos requeridos por la herramienta.

    Returns:
        Resultado de la ejecución de la herramienta (puede ser cualquier tipo).
    """
    tools = get_tools()
    if tool_name not in tools:
        raise ValueError(f"La herramienta '{tool_name}' no está registrada o no está activa.")
    
    func = tools[tool_name]["func"]
    return func(**arguments)
