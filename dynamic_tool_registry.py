import os
import json
from datetime import datetime

TOOLS_FOLDER = "tools"
dynamic_tools = {}

# Asegurarse de que el directorio de debug existe
debug_dir = "debug_logs"
if not os.path.exists(debug_dir):
    os.makedirs(debug_dir, exist_ok=True)

def register_tool(name: str, schema: dict, func_code: str):
    # Registrar diagnóstico en el archivo de debug
    with open("debug_logs/file_creation_debug.log", "a") as debug_file:
        debug_file.write(f"\n\n--- NUEVA LLAMADA A register_tool {datetime.now().isoformat()} ---\n")
        debug_file.write(f"Nombre: {name}\n")
        debug_file.write(f"Schema: {json.dumps(schema, indent=2, ensure_ascii=False)}\n")
        debug_file.write(f"Longitud de func_code: {len(func_code)} caracteres\n")
        debug_file.write(f"Primeras líneas de func_code: {func_code.split('\\n')[:3]}\n")
        
        try:
            namespace = {}
            debug_file.write(f"Ejecutando código en namespace...\n")
            exec(func_code, namespace)
            
            debug_file.write(f"Keys en namespace: {list(namespace.keys())}\n")
            
            if name not in namespace:
                error_msg = f"La función '{name}' no está definida en el código"
                debug_file.write(f"ERROR: {error_msg}\n")
                raise ValueError(error_msg)
                
            debug_file.write(f"Función '{name}' encontrada en el namespace\n")
            
            dynamic_tools[name] = {
                "schema": schema,
                "func": namespace[name],
                "code": func_code
            }
            
            debug_file.write(f"Herramienta '{name}' registrada con éxito en memoria\n")
            
        except ModuleNotFoundError as e:
            error_msg = f"Falta un módulo requerido: {e.name}"
            debug_file.write(f"ERROR (ModuleNotFoundError): {error_msg}\n")
            raise ImportError(f"Falta un módulo requerido: {e.name}. Instálalo con 'pip install {e.name}'") from e
        except Exception as e:
            error_msg = f"Error al registrar la tool '{name}': {str(e)}"
            debug_file.write(f"ERROR (Exception): {error_msg}\n")
            import traceback
            debug_file.write(f"TRACEBACK: {traceback.format_exc()}\n")
            raise RuntimeError(error_msg) from e

def get_all_dynamic_tools():
    return dynamic_tools

def get_dynamic_tool(name):
    return dynamic_tools.get(name)

def persist_tool_to_disk(name: str, schema: dict, func_code: str):
    # Crear un registro detallado de depuración
    with open("debug_logs/file_creation_debug.log", "a") as debug_file:
        debug_file.write(f"\n\n--- NUEVA LLAMADA A persist_tool_to_disk {datetime.now().isoformat()} ---\n")
        debug_file.write(f"Nombre: {name}\n")
        debug_file.write(f"Ruta de trabajo: {os.getcwd()}\n")
        debug_file.write(f"Existe TOOLS_FOLDER '{TOOLS_FOLDER}': {os.path.exists(TOOLS_FOLDER)}\n")
        
        try:
            # Asegurarse de que la carpeta existe
            os.makedirs(TOOLS_FOLDER, exist_ok=True)
            debug_file.write(f"Carpeta creada/verificada\n")
            
            # Ruta completa del archivo
            path = os.path.join(TOOLS_FOLDER, f"{name}.py")
            debug_file.write(f"Ruta del archivo a crear: {path}\n")
            
            # Verificar si el func_code ya contiene una definición de schema
            has_schema = "schema = " in func_code or "schema=" in func_code
            debug_file.write(f"¿El código ya tiene schema?: {has_schema}\n")
            
            try:
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
                        json_schema = json.dumps(schema, indent=2, ensure_ascii=False)
                        f.write(json_schema + "\n")
                
                # Verificar que el archivo se creó correctamente
                exists = os.path.exists(path)
                debug_file.write(f"¿Se creó el archivo?: {exists}\n")
                debug_file.write(f"Tamaño del archivo: {os.path.getsize(path) if exists else 'N/A'}\n")
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