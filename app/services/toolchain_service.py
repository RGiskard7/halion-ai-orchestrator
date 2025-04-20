"""
toolchain_service.py

Módulo encargado de ejecutar una Toolchain paso por paso, usando el contexto acumulado
como entrada y salida entre pasos.

Cada paso llama a una herramienta específica, utilizando los valores del contexto previo.
"""

import time
from typing import Any, Dict, Tuple, List
from app.core import toolchain_registry
from app.core.tool_manager import get_tools
from app.models.toolchain_model import Toolchain, ToolchainStep
from app.utils.ai_generation import generate_toolchain_with_ai

# --- Servicio de Ejecución de Toolchains ---

def execute_toolchain(toolchain_name: str, initial_context: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Ejecuta una toolchain paso a paso.

    Args:
        toolchain_name (str): Nombre de la toolchain a ejecutar.
        initial_context (Dict[str, Any]): Diccionario con los inputs iniciales.

    Returns:
        Tuple[Dict[str, Any], List[Dict[str, Any]]]:
            - El contexto final después de ejecutar todos los pasos.
            - Una lista de diccionarios, cada uno representando el log de un paso.

    Raises:
        ValueError: Si la toolchain no se encuentra.
        Exception: Si ocurre un error durante la ejecución de un paso.
    """
    # Obtener la definición de la toolchain
    # Asegurarse de cargar la última versión desde disco
    toolchain_registry.load_toolchains_from_disk()
    toolchain = toolchain_registry.get_toolchain(toolchain_name)
    if not toolchain:
        raise ValueError(f"Toolchain '{toolchain_name}' no encontrada en el registro.")

    # Obtener las herramientas disponibles
    available_tools = get_tools()

    # Inicializar contexto y log de pasos
    current_context = initial_context.copy()
    steps_log = []

    print(f"[Toolchain Service] Iniciando ejecución de '{toolchain_name}' con contexto: {current_context}")

    # Ejecutar cada paso
    for i, step in enumerate(toolchain.steps):
        step_number = i + 1
        step_start_time = time.time()
        step_log_entry = {
            "step": step_number,
            "tool_name": step.tool_name,
            "status": "PENDING",
            "inputs": {},
            "output": None,
            "error": None,
            "duration_seconds": 0
        }

        print(f"[Toolchain Service] Paso {step_number}: Ejecutando tool '{step.tool_name}'")

        try:
            # Mapear inputs desde el contexto actual
            inputs_for_step = {}
            missing_keys = []
            for param_name, context_key in step.input_map.items():
                if context_key in current_context:
                    inputs_for_step[param_name] = current_context[context_key]
                else:
                    # Permitir que falten claves? O fallar? Por ahora, fallamos.
                    missing_keys.append(context_key)

            step_log_entry["inputs"] = inputs_for_step

            if missing_keys:
                raise ValueError(f"Faltan las siguientes claves en el contexto para mapear inputs del paso {step_number} ('{step.tool_name}'): {', '.join(missing_keys)}")

            # Encontrar la función de la herramienta
            tool_info = available_tools.get(step.tool_name)
            if not tool_info or "func" not in tool_info:
                raise LookupError(f"La herramienta '{step.tool_name}' (requerida en paso {step_number}) no está disponible o no tiene una función ejecutable.")

            tool_function = tool_info["func"]

            # Ejecutar la herramienta
            print(f"[Toolchain Service] Paso {step_number}: Llamando a {step.tool_name} con args: {inputs_for_step}")
            output = tool_function(**inputs_for_step)
            step_end_time = time.time()
            step_log_entry["duration_seconds"] = round(step_end_time - step_start_time, 4)

            # Asegurarse de que el output sea un diccionario para actualizar el contexto
            if output is not None and not isinstance(output, dict):
                 print(f"[Toolchain Service] Paso {step_number}: Output de {step.tool_name} no es dict ({type(output)}), envolviendo en {{'{step.tool_name}_result': ...}}")
                 # Usar un nombre de clave más específico basado en la tool
                 output = {f"{step.tool_name}_result": output}
            elif output is None:
                 # Si la tool devuelve None, no actualizamos el contexto con ello
                 print(f"[Toolchain Service] Paso {step_number}: {step.tool_name} devolvió None. No se actualiza el contexto.")
                 output = {} # Usar un dict vacío para la consistencia del log

            # Actualizar el contexto con el output (si no es None)
            if output:
                 current_context.update(output)

            step_log_entry["output"] = output
            step_log_entry["status"] = "SUCCESS"
            print(f"[Toolchain Service] Paso {step_number}: Éxito. Output: {output}. Contexto actualizado: {current_context}")


        except Exception as e:
            step_end_time = time.time()
            step_log_entry["duration_seconds"] = round(step_end_time - step_start_time, 4)
            step_log_entry["status"] = "ERROR"
            step_log_entry["error"] = str(e)
            steps_log.append(step_log_entry) # Añadir el log del paso fallido
            print(f"[Toolchain Service] Paso {step_number}: Error ejecutando {step.tool_name}: {e}")
            # Propagar la excepción para que el controlador la maneje
            raise Exception(f"Error en el paso {step_number} ('{step.tool_name}'): {e}")

        steps_log.append(step_log_entry)

    print(f"[Toolchain Service] Ejecución de '{toolchain_name}' completada. Contexto final: {current_context}")
    return current_context, steps_log

# --- Servicio de Generación de Toolchains con IA ---

def generate_toolchain_via_ai(description: str, api_key: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Llama a la utilidad de generación de toolchains por IA.

    Args:
        description (str): Descripción en lenguaje natural de la toolchain.
        api_key (str): Clave API de OpenAI.
        model_config (Dict[str, Any]): Configuración del modelo (nombre, temperatura, etc.).

    Returns:
        Dict[str, Any]: La estructura de la toolchain generada en formato diccionario.

    Raises:
        ValueError: Si falta la API key.
        Exception: Si la generación falla por cualquier motivo.
    """
    if not api_key:
        raise ValueError("Se requiere una API key de OpenAI para la generación con IA.")

    print(f"[Toolchain Service] Solicitando generación de toolchain con IA para descripción: \"{description[:50]}...\"")
    try:
        # Extraer parámetros relevantes para la función de generación
        model_name = model_config.get("model", "gpt-4") # Usar un default razonable
        temperature = model_config.get("temperature", 0.7) # Default razonable

        # Llamar a la función real de generación
        # Asegurarse de que la función ai_generation existe y es importada correctamente
        generated_toolchain_data = generate_toolchain_with_ai(
            prompt=description,
            api_key=api_key,
            model=model_name,
            temperature=temperature
        )

        # Validar mínimamente la estructura devuelta?
        if not isinstance(generated_toolchain_data, dict) or "name" not in generated_toolchain_data or "steps" not in generated_toolchain_data:
             print(f"[Toolchain Service] WARNING: La estructura generada por IA parece incompleta: {generated_toolchain_data}")
             # Podríamos lanzar un error o devolverla tal cual
             # raise ValueError("La estructura generada por IA no es válida (falta 'name' o 'steps').")

        print(f"[Toolchain Service] Toolchain generada por IA: {generated_toolchain_data}")
        return generated_toolchain_data
    except Exception as e:
        print(f"[Toolchain Service] Error durante la generación de toolchain por IA: {e}")
        # Podríamos querer loggear más detalles aquí
        raise Exception(f"Error al generar la toolchain con IA: {e}")
