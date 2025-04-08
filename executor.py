import openai
import json
from logger import log_tool_call
from tool_manager import get_tools

def chat_with_tools(prompt: str, user_id="anon", api_key="", model="gpt-4", temperature=0.7):
    openai.api_key = api_key
    all_tools = get_tools()
    schemas = [info["schema"] for info in all_tools.values()]

    messages = [{"role": "user", "content": prompt}]

    # Primera llamada
    if schemas:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            functions=schemas,
            function_call="auto",
            temperature=temperature
        )
    else:
        # Sin tools definidas
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )

    reply = response.choices[0].message

    if hasattr(reply, "function_call") and reply.function_call:
        func_name = reply.function_call.name
        arguments = json.loads(reply.function_call.arguments)

        if func_name in all_tools:
            # Ejecutar tool
            result = all_tools[func_name]["func"](**arguments)
            log_tool_call(func_name, arguments, result)

            # Siempre pasamos por el modelo, pero con instrucciones específicas
            messages.append(reply.to_dict())
            messages.append({"role": "function", "name": func_name, "content": result})

            # Si la herramienta no requiere post-procesamiento, damos instrucciones específicas
            if not all_tools[func_name]["schema"].get("postprocess", True):
                messages.append({
                    "role": "system",
                    "content": "Por favor, devuelve el resultado exacto de la herramienta sin modificarlo ni resumirlo, pero evalúa si se necesitan llamadas adicionales a otras herramientas."
                })

            final = openai.chat.completions.create(
                model=model,
                messages=messages,
                functions=schemas,  # Mantenemos la posibilidad de llamadas adicionales
                function_call="auto",
                temperature=temperature
            )
            return final.choices[0].message.content
        else:
            return f"La función '{func_name}' no existe."
    else:
        return reply.content