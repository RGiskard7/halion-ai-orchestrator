# app/services/tool_service.py

from typing import Dict, Any, Tuple, List, Optional
import os

# Importar utilidades y core necesarios
from app.utils.ai_generation import generate_tool_with_ai
from app.utils.env_detection import detect_env_variables
from app.core.env_manager import get_env_variables, set_env_variable, reload_env_variables

def generate_tool_code_via_ai(description: str, api_key: str, model_config: Dict[str, Any]) -> str:
    """
    Llama a la utilidad de generación de código de tool por IA.

    Args:
        description (str): Descripción en lenguaje natural de la tool.
        api_key (str): Clave API de OpenAI.
        model_config (Dict[str, Any]): Configuración del modelo (nombre, temperatura, etc.).

    Returns:
        str: El código Python generado para la tool.

    Raises:
        ValueError: Si falta la API key.
        Exception: Si la generación falla por cualquier motivo.
    """
    print(f"[Tool Service] Solicitando generación de código de tool con IA para: \"{description[:50]}...\"")
    if not api_key:
        raise ValueError("Se requiere una API key de OpenAI para la generación con IA.")

    try:
        model_name = model_config.get("model", "gpt-4")
        temperature = model_config.get("temperature", 0.7)

        generated_code = generate_tool_with_ai(
            description=description,
            api_key=api_key,
            model=model_name,
            temperature=temperature
        )
        print(f"[Tool Service] Código de tool generado por IA (primeras 100 chars): {generated_code[:100]}...")
        return generated_code
    except Exception as e:
        print(f"[Tool Service] Error durante la generación de código de tool por IA: {e}")
        raise Exception(f"Error al generar el código de la tool con IA: {e}")


def extract_tool_metadata_and_env_vars(code: str) -> Tuple[Optional[str], Optional[Dict], Optional[List[Dict]]]:
    """
    Ejecuta el código generado para extraer nombre, schema y detecta variables de entorno.

    Args:
        code (str): El código Python de la herramienta generada.

    Returns:
        Tuple[Optional[str], Optional[Dict], Optional[List[Dict]]]:
            - Nombre de la función/tool detectada (o None).
            - Diccionario del schema detectado (o None).
            - Lista de diccionarios de variables de entorno detectadas (o None).
            Devuelve Nones en caso de error.
    """
    print("[Tool Service] Extrayendo metadatos y variables de entorno del código generado...")
    tool_name: Optional[str] = None
    schema: Optional[Dict] = None
    detected_env_vars: Optional[List[Dict]] = None

    try:
        # Ejecutar código para obtener schema y nombre
        namespace = {}
        exec(code, namespace)

        # Buscar la función y el schema
        extracted_schema = namespace.get("schema")
        if isinstance(extracted_schema, dict):
             schema = extracted_schema
             # Intentar obtener el nombre desde el schema primero
             tool_name = schema.get("name")
             if not tool_name:
                 # Si no está en el schema, buscar la función callable
                 for name, obj in namespace.items():
                     if callable(obj) and name != 'exec' and not name.startswith('__'):
                         tool_name = name
                         break
                 if tool_name:
                      print(f"[Tool Service] Nombre de tool inferido de función: {tool_name}")
                 else:
                      print("[Tool Service] WARNING: No se pudo determinar el nombre de la tool desde el código.")
             else:
                 print(f"[Tool Service] Nombre de tool obtenido del schema: {tool_name}")
        else:
            print("[Tool Service] WARNING: No se encontró un diccionario 'schema' en el código generado.")

        # Detectar variables de entorno
        detected_env_vars = detect_env_variables(code)
        print(f"[Tool Service] Variables de entorno detectadas: {[v['name'] for v in detected_env_vars] if detected_env_vars else []}")

        return tool_name, schema, detected_env_vars

    except Exception as e:
        print(f"[Tool Service] Error al extraer metadatos o detectar env vars: {e}")
        import traceback
        print(traceback.format_exc())
        # Devolver Nones si hay error
        return None, None, None


def save_detected_env_vars(detected_env_vars_with_values: List[Dict]) -> Tuple[List[str], List[str]]:
    """
    Guarda las variables de entorno detectadas (con valores potencialmente añadidos) en el archivo .env.

    Args:
        detected_env_vars_with_values (List[Dict]): Lista de diccionarios, donde cada
            diccionario representa una variable y puede tener la clave "value".

    Returns:
        Tuple[List[str], List[str]]:
            - Lista de nombres de variables guardadas/actualizadas.
            - Lista de nombres de variables existentes cuyo valor no cambió.

    Raises:
        Exception: Si ocurre un error al interactuar con env_manager.
    """
    print(f"[Tool Service] Intentando guardar {len(detected_env_vars_with_values)} variables de entorno detectadas...")
    vars_saved_or_updated: List[str] = []
    vars_unchanged: List[str] = []

    if not detected_env_vars_with_values:
        return vars_saved_or_updated, vars_unchanged

    try:
        existing_env_vars = get_env_variables()

        for var_info in detected_env_vars_with_values:
            var_name = var_info.get("name")
            new_value = var_info.get("value") # Puede ser None o ""

            if not var_name:
                print("[Tool Service] WARNING: Se omitió una variable detectada sin nombre.")
                continue

            # Comparar con valor existente
            if var_name in existing_env_vars:
                # Si el nuevo valor no se proporcionó O es igual al existente, no hacer nada.
                if new_value is None or new_value == existing_env_vars[var_name]:
                    vars_unchanged.append(var_name)
                    continue

            # Guardar la variable (nueva o actualizada)
            print(f"[Tool Service] Guardando/Actualizando variable: {var_name}")
            if set_env_variable(var_name, new_value if new_value is not None else ""):
                vars_saved_or_updated.append(var_name)
            else:
                # Si set_env_variable falla, podría lanzar una excepción o devolver False
                # Dependiendo de la implementación de env_manager. Asumimos que False indica fallo.
                print(f"[Tool Service] ERROR: Falló el guardado de la variable {var_name}")
                # ¿Deberíamos parar o continuar? Por ahora continuamos.

        # Recargar variables si alguna cambió
        if vars_saved_or_updated:
            print("[Tool Service] Recargando variables de entorno...")
            reload_env_variables()

        print(f"[Tool Service] Variables guardadas/actualizadas: {vars_saved_or_updated}")
        print(f"[Tool Service] Variables sin cambios: {vars_unchanged}")
        return vars_saved_or_updated, vars_unchanged

    except Exception as e:
        print(f"[Tool Service] Error al guardar variables de entorno: {e}")
        import traceback
        print(traceback.format_exc())
        # Propagar la excepción para que el controlador la maneje
        raise Exception(f"Error durante el guardado de variables de entorno: {e}") 