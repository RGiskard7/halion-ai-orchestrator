# env_manager.py
import os
from dotenv import dotenv_values, set_key, unset_key, load_dotenv
import logging

ENV_PATH = ".env"

def get_env_variables():
    """
    Obtiene todas las variables de entorno del archivo .env
    """
    # Asegurarse de que existe el archivo
    if not os.path.exists(ENV_PATH):
        # Crear un archivo vacío
        with open(ENV_PATH, 'w') as f:
            pass
    return dotenv_values(ENV_PATH)

def reload_env_variables():
    """
    Recarga las variables de entorno en tiempo de ejecución
    """
    # Volver a cargar el archivo .env
    load_dotenv(ENV_PATH, override=True)
    
    # También actualizar explícitamente os.environ con las nuevas variables
    env_vars = dotenv_values(ENV_PATH)
    for key, value in env_vars.items():
        os.environ[key] = value
    
    return env_vars

def set_env_variable(key, value):
    """
    Establece o actualiza una variable de entorno en el archivo .env
    
    Args:
        key: Nombre de la variable
        value: Valor a establecer (puede ser vacío)
    """
    # Asegurarse de que existe el archivo
    if not os.path.exists(ENV_PATH):
        # Crear un archivo vacío
        with open(ENV_PATH, 'w') as f:
            pass
    
    try:
        # Enfoque directo que funciona con valores vacíos
        # Leer el archivo actual
        content = ""
        if os.path.exists(ENV_PATH) and os.path.getsize(ENV_PATH) > 0:
            with open(ENV_PATH, 'r') as f:
                content = f.read()
        
        # Convertir el contenido en líneas
        lines = content.splitlines() if content else []
        
        # Buscar si la variable ya existe
        var_exists = False
        new_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Ignorar líneas vacías y comentarios
                if line.startswith(f"{key}="):
                    # Reemplazar la línea existente
                    new_lines.append(f"{key}={value}")
                    var_exists = True
                else:
                    new_lines.append(line)
            else:
                # Mantener comentarios y líneas vacías
                new_lines.append(line)
        
        # Si no existe, añadirla al final
        if not var_exists:
            new_lines.append(f"{key}={value}")
        
        # Escribir el archivo actualizado
        with open(ENV_PATH, 'w') as f:
            f.write('\n'.join(new_lines))
            # Asegurar que hay una línea vacía al final
            if new_lines:
                f.write('\n')
        
        logging.info(f"Variable de entorno {key} guardada exitosamente")
        return True
        
    except Exception as e:
        logging.error(f"Error al establecer variable de entorno {key}: {str(e)}")
        # Intentar un enfoque más básico como último recurso
        try:
            with open(ENV_PATH, 'a') as f:
                f.write(f"{key}={value}\n")
            return True
        except Exception as inner_e:
            logging.error(f"Error crítico al establecer variable: {str(inner_e)}")
            return False

def delete_env_variable(key):
    """
    Elimina una variable de entorno del archivo .env
    """
    if os.path.exists(ENV_PATH):
        unset_key(ENV_PATH, key)