import openai
import json
from app.core.logger import log_tool_call
from app.core.tool_manager import get_tools

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
            result = all_tools[func_name]["func"](**arguments)
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

            # Si la herramienta no requiere post-procesamiento, damos instrucciones específicas
            '''if not all_tools[func_name]["schema"].get("postprocess", True):
                messages.append({
                    "role": "system",
                    "content": "Por favor, devuelve el resultado exacto de la herramienta sin modificarlo ni resumirlo, pero evalúa si se necesitan llamadas adicionales a otras herramientas."
                })'''

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