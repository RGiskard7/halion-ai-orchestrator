'''
Este archivo es el encargado de registrar las herramientas dinámicas en memoria.

La lógica de este archivo es la siguiente:

1. Carga todas las herramientas dinámicas desde el directorio tools
2. Registra cada herramienta dinámica en memoria
3. Devuelve las herramientas dinámicas activas
'''

import os
import json
from datetime import datetime

# Definir rutas absolutas basadas en la ubicación actual del script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)    # Directorio app/
ROOT_DIR = os.path.dirname(APP_DIR)       # Directorio raíz del proyecto

TOOLS_FOLDER = os.path.join(APP_DIR, "tools")
DEBUG_LOGS_FOLDER = os.path.join(APP_DIR, "debug_logs")

dynamic_tools = {}

# Asegurarse de que el directorio de debug existe
os.makedirs(DEBUG_LOGS_FOLDER, exist_ok=True)

# Asegurarse de que el directorio tools existe
os.makedirs(TOOLS_FOLDER, exist_ok=True)

# --- Funciones de gestión de archivos de herramientas --- #

def get_tool_code(tool_name: str) -> str | None:
    """Lee y devuelve el código fuente de un archivo de herramienta."""
    tool_path = os.path.join(TOOLS_FOLDER, f"{tool_name}.py")
    try:
        if os.path.exists(tool_path):
            with open(tool_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return None # O lanzar FileNotFoundError?
    except IOError as e:
        print(f"[ERROR] No se pudo leer el archivo {tool_path}: {e}")
        return None # O lanzar excepción

def save_tool_code(tool_name: str, code: str) -> bool:
    """Guarda o sobrescribe el código fuente de un archivo de herramienta."""
    tool_path = os.path.join(TOOLS_FOLDER, f"{tool_name}.py")
    try:
        os.makedirs(os.path.dirname(tool_path), exist_ok=True)
        with open(tool_path, "w", encoding="utf-8") as f:
            f.write(code)
        return True
    except IOError as e:
        print(f"[ERROR] No se pudo guardar el archivo {tool_path}: {e}")
        return False

def delete_tool_file(tool_name: str) -> bool:
    """Elimina el archivo .py de una herramienta."""
    tool_path = os.path.join(TOOLS_FOLDER, f"{tool_name}.py")
    try:
        if os.path.exists(tool_path):
            os.remove(tool_path)
            print(f"[INFO] Archivo eliminado: {tool_path}")
            return True
        else:
            print(f"[WARN] El archivo a eliminar no existe: {tool_path}")
            return False # Indicar que no se hizo nada porque no existía?
    except OSError as e:
        print(f"[ERROR] No se pudo eliminar el archivo {tool_path}: {e}")
        return False

# --- Funciones de registro y persistencia existentes --- #

def register_tool(name: str, schema: dict, func_code: str):
    # Ruta al archivo de logs
    debug_log_path = os.path.join(DEBUG_LOGS_FOLDER, "file_creation_debug.log")
    
    # Registrar diagnóstico en el archivo de debug
    with open(debug_log_path, "a") as debug_file:
        debug_file.write(f"\n\n--- NUEVA LLAMADA A register_tool {datetime.now().isoformat()} ---\n")
        debug_file.write(f"Nombre recibido como parámetro: {name}\n")
        
        # Usar el nombre correcto desde el schema
        tool_name = schema.get("name", name)
        debug_file.write(f"Nombre correcto extraído del schema: {tool_name}\n")
        debug_file.write(f"Ruta actual del script: {CURRENT_DIR}\n")
        debug_file.write(f"Ruta de la app: {APP_DIR}\n")
        debug_file.write(f"Ruta de herramientas: {TOOLS_FOLDER}\n")
        debug_file.write(f"Existe TOOLS_FOLDER: {os.path.exists(TOOLS_FOLDER)}\n")
        debug_file.write(f"Schema: {json.dumps(schema, indent=2, ensure_ascii=False)}\n")
        debug_file.write(f"Longitud de func_code: {len(func_code)} caracteres\n")
        debug_file.write(f"Primeras líneas de func_code: {repr(func_code.splitlines()[:3])}\n")
        
        try:
            namespace = {}
            debug_file.write(f"Ejecutando código en namespace...\n")
            exec(func_code, namespace)
            
            debug_file.write(f"Keys en namespace: {list(namespace.keys())}\n")
            
            # Buscar la función con el nombre correcto (desde schema)
            func_callable = None
            for func_name, obj in namespace.items():
                if callable(obj) and func_name == tool_name:
                    func_callable = obj
                    debug_file.write(f"Función '{tool_name}' encontrada en el namespace\n")
                    break
            
            # Si no la encontramos por nombre exacto, entonces intentamos encontrar cualquier callable
            if not func_callable:
                debug_file.write(f"No se encontró la función '{tool_name}' exacta, buscando cualquier callable...\n")
                for func_name, obj in namespace.items():
                    if callable(obj) and func_name != 'exec' and not func_name.startswith('__'):
                        func_callable = obj
                        debug_file.write(f"Usando función alternativa '{func_name}' encontrada en el namespace\n")
                        break
            
            if not func_callable:
                error_msg = f"No se encontró ninguna función llamable en el código"
                debug_file.write(f"ERROR: {error_msg}\n")
                raise ValueError(error_msg)
            
            # Guardar la herramienta en memoria usando el nombre correcto
            dynamic_tools[tool_name] = {
                "schema": schema,
                "func": func_callable,
                "code": func_code
            }
            
            debug_file.write(f"Herramienta '{tool_name}' registrada con éxito en memoria\n")
            
            # Devolver el nombre correcto
            return tool_name
            
        except ModuleNotFoundError as e:
            error_msg = f"Falta un módulo requerido: {e.name}"
            debug_file.write(f"ERROR (ModuleNotFoundError): {error_msg}\n")
            raise ImportError(f"Falta un módulo requerido: {e.name}. Instálalo con 'pip install {e.name}'") from e
        except Exception as e:
            error_msg = f"Error al registrar la tool '{tool_name}': {str(e)}"
            debug_file.write(f"ERROR (Exception): {error_msg}\n")
            import traceback
            debug_file.write(f"TRACEBACK: {traceback.format_exc()}\n")
            raise RuntimeError(error_msg) from e

def get_all_dynamic_tools():
    return dynamic_tools

def get_dynamic_tool(name):
    return dynamic_tools.get(name)

def persist_tool_to_disk(name: str, schema: dict, func_code: str):
    # Ruta al archivo de logs
    debug_log_path = os.path.join(DEBUG_LOGS_FOLDER, "file_creation_debug.log")
    
    # Crear un registro detallado de depuración
    with open(debug_log_path, "a") as debug_file:
        debug_file.write(f"\n\n--- NUEVA LLAMADA A persist_tool_to_disk {datetime.now().isoformat()} ---\n")
        debug_file.write(f"Nombre recibido: {name}\n")
        
        # Usar el nombre de la herramienta desde el schema, que es más confiable
        tool_name = schema.get("name", name)
        debug_file.write(f"Nombre de herramienta en schema: {tool_name}\n")
        
        debug_file.write(f"Ruta de trabajo actual: {os.getcwd()}\n")
        debug_file.write(f"Ruta actual del script: {CURRENT_DIR}\n")
        debug_file.write(f"Ruta de la app: {APP_DIR}\n")
        debug_file.write(f"Ruta de herramientas: {TOOLS_FOLDER}\n")
        debug_file.write(f"Existe TOOLS_FOLDER: {os.path.exists(TOOLS_FOLDER)}\n")
        
        # Comprobar permisos
        try:
            debug_file.write(f"Verificando permisos de escritura en {TOOLS_FOLDER}...\n")
            if os.access(TOOLS_FOLDER, os.W_OK):
                debug_file.write(f"✅ El directorio tiene permisos de escritura\n")
            else:
                debug_file.write(f"❌ El directorio NO tiene permisos de escritura\n")
        except Exception as perm_e:
            debug_file.write(f"Error al verificar permisos: {str(perm_e)}\n")
        
        try:
            # Asegurarse de que la carpeta existe
            debug_file.write(f"Intentando crear el directorio {TOOLS_FOLDER} si no existe...\n")
            os.makedirs(TOOLS_FOLDER, exist_ok=True)
            debug_file.write(f"Carpeta creada/verificada: {TOOLS_FOLDER}\n")
            debug_file.write(f"Después de crear, ¿existe TOOLS_FOLDER?: {os.path.exists(TOOLS_FOLDER)}\n")
            
            # Ruta completa del archivo usando el nombre correcto de la herramienta
            path = os.path.join(TOOLS_FOLDER, f"{tool_name}.py")
            debug_file.write(f"Ruta del archivo a crear: {path}\n")
            
            # Verificar si el func_code ya contiene una definición de schema
            has_schema = "schema = " in func_code or "schema=" in func_code
            debug_file.write(f"¿El código ya tiene schema?: {has_schema}\n")
            
            try:
                # Asegurarse de que el directorio existe (otra vez, por seguridad)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                debug_file.write(f"Verificado directorio de destino: {os.path.dirname(path)}\n")
                
                debug_file.write(f"Intentando escribir el archivo {path}...\n")
                
                if has_schema:
                    # El código ya tiene schema, guardarlo tal cual
                    debug_file.write(f"Guardando archivo con schema existente...\n")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(func_code.strip() + "\n")
                else:
                    # El código no tiene schema, añadirlo
                    debug_file.write(f"Guardando archivo añadiendo schema...\n")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(func_code.strip() + "\n\n")
                        f.write("schema = ")
                        # Usar repr() para obtener una representación de string Python válida del schema
                        python_repr_schema = repr(schema)
                        f.write(python_repr_schema + "\n")
                
                # Verificar que el archivo se creó correctamente
                exists = os.path.exists(path)
                debug_file.write(f"¿Se creó el archivo?: {exists}, ruta: {path}\n")
                if exists:
                    file_size = os.path.getsize(path)
                    debug_file.write(f"Tamaño del archivo: {file_size} bytes\n")
                    
                    # Verificar contenido
                    try:
                        with open(path, "r", encoding="utf-8") as check_file:
                            first_line = check_file.readline().strip()
                            debug_file.write(f"Primera línea del archivo creado: {first_line}\n")
                    except Exception as read_e:
                        debug_file.write(f"Error al leer el archivo creado: {str(read_e)}\n")
                else:
                    debug_file.write(f"ADVERTENCIA: El archivo no existe después de intentar crearlo\n")
                
                # Listar archivos en el directorio para verificar
                try:
                    files_in_dir = os.listdir(os.path.dirname(path))
                    debug_file.write(f"Archivos en el directorio después de crear: {files_in_dir}\n")
                except Exception as list_e:
                    debug_file.write(f"Error al listar archivos: {str(list_e)}\n")
                
                # Devolver True si el archivo existe después de intentar escribir
                if not exists:
                     print(f"[ERROR] Falló la escritura del archivo {path}")

                return exists
                
            except Exception as e:
                debug_file.write(f"ERROR AL ESCRIBIR EL ARCHIVO: {str(e)}\n")
                import traceback
                debug_file.write(f"TRACEBACK: {traceback.format_exc()}\n")
                return False
                
        except Exception as outer_e:
            debug_file.write(f"ERROR GENERAL: {str(outer_e)}\n")
            import traceback
            debug_file.write(f"TRACEBACK GENERAL: {traceback.format_exc()}\n")
            return False 