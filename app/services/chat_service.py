"""
chat_services.py

Servicio principal de interacción entre el modelo de OpenAI y las herramientas individuales registradas,
utilizando la capacidad de "function calling" de OpenAI.

Depende de:
- tool_manager: para cargar y ejecutar tools.

HALion, 2025
"""

import openai
import json
from app.core.logger import log_tool_call
from app.core.tool_manager import get_tools, call_tool_by_name

def chat_with_tools(
    prompt: str, 
    user_id="anon", 
    api_key="", 
    model="gpt-4o-mini", 
    temperature=0.7, 
    max_tokens=None, 
    top_p=1.0, 
    presence_penalty=0.0, 
    frequency_penalty=0.0, 
    seed=None
):
    """
    Función principal que coordina la interacción con el modelo de OpenAI y 
    ejecuta herramientas según sea necesario.
    """
    
    # === Flujo habitual ===
    openai.api_key = api_key
    all_tools = get_tools()
    schemas = [info["schema"] for info in all_tools.values()]
    
    # Crear diccionario base para parámetros comunes
    common_params = {
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty
    }
    
    # Añadir parámetros opcionales solo si se proporcionan
    if max_tokens:
        common_params["max_tokens"] = max_tokens
    if seed is not None:
        common_params["seed"] = seed

    messages = [{"role": "user", "content": prompt}]

    # Primera llamada
    if schemas:
        response = openai.chat.completions.create(
            **common_params,
            messages=messages,
            functions=schemas,
            function_call="auto"
        )
    else:
        # Sin tools definidas
        response = openai.chat.completions.create(
            **common_params,
            messages=messages
        )

    reply = response.choices[0].message

    if hasattr(reply, "function_call") and reply.function_call:
        func_name = reply.function_call.name
        arguments = json.loads(reply.function_call.arguments)

        if func_name in all_tools:
            # Ejecutar tool
            result = call_tool_by_name(func_name, arguments)
            log_tool_call(func_name, arguments, result)

            # Convertir el resultado a string si no lo es ya
            if not isinstance(result, str):
                result = json.dumps(result, ensure_ascii=False, indent=2)

            # Si no requiere post-proceso, devuelve el resultado tal cual
            if not all_tools[func_name]["schema"].get("postprocess", True):
                return result
            
            # Si sí requiere postproceso, sigue el flujo habitual
            messages.append(reply.to_dict())
            messages.append({"role": "function", "name": func_name, "content": result})

            final = openai.chat.completions.create(
                **common_params,
                messages=messages,
                functions=schemas,  # Mantenemos la posibilidad de llamadas adicionales
                function_call="auto"
            )
            return final.choices[0].message.content
        else:
            return f"La función '{func_name}' no existe."
    else:
        return reply.content