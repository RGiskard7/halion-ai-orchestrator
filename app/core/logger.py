# logger.py (completo y actualizado)
import json
from datetime import datetime
import os

# Definir rutas absolutas basadas en la ubicación actual del script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)         # Directorio app/
ROOT_DIR = os.path.dirname(APP_DIR)            # Directorio raíz del proyecto
DEBUG_LOGS_DIR = os.path.join(APP_DIR, "debug_logs")  # Directorio app/debug_logs/

# Asegurar que el directorio debug_logs existe
if not os.path.exists(DEBUG_LOGS_DIR):
    os.makedirs(DEBUG_LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(DEBUG_LOGS_DIR, "tool_calls.log")

def log_tool_call(function_name: str, arguments: dict, result):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "function": function_name,
        "arguments": arguments,
        "result": result
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def load_log_entries(limit: int = 100):
    """
    Carga entradas de log desde el archivo de logs.
    
    Args:
        limit: Número máximo de entradas a cargar
        
    Returns:
        list: Lista de entradas de log como diccionarios
    """
    try:
        # Verificar si existe el archivo en la ubicación nueva
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, encoding="utf-8") as f:
                lines = f.readlines()[-limit:]
                return [json.loads(line.strip()) for line in lines]
        else:
            # Verificar si existe en la ubicación antigua
            old_log_file = os.path.join(ROOT_DIR, "tool_calls.log")
            if os.path.exists(old_log_file):
                # Leer el archivo antiguo
                with open(old_log_file, encoding="utf-8") as f:
                    lines = f.readlines()
                
                # Migrar a la nueva ubicación
                with open(LOG_FILE, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                
                # Eliminar el archivo antiguo
                os.remove(old_log_file)
                
                # Devolver los datos migrados (limitados)
                return [json.loads(line.strip()) for line in lines[-limit:]]
        
        # Si no existe en ninguna ubicación
        return []
    except FileNotFoundError:
        return []

def clear_log_entries():
    open(LOG_FILE, "w").close()

def export_logs_json():
    return json.dumps(load_log_entries(), indent=2, ensure_ascii=False)

def export_logs_csv():
    import pandas as pd
    logs = load_log_entries()
    return pd.DataFrame(logs).to_csv(index=False)