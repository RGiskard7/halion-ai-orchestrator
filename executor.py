import openai
import json
import os
from dotenv import load_dotenv
from tool_manager import get_tools_for_user_object
from logger import log_tool_call

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def chat_with_tools(user_input: str, user_id):
    tools = get_tools_for_user_object(user_id)
    function_schemas = [tools[name]["schema"] for name in tools]

    messages = [{"role": "user", "content": user_input}]

    if function_schemas:
        # Llamada con 'functions' y 'function_call'
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            functions=function_schemas,
            function_call="auto"
        )
    else:
        # Llamada normal sin funciones
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

    message = response.choices[0].message

    # Manejo de function_call solo si hay tools
    if function_schemas and hasattr(message, "function_call") and message.function_call:
        func_name = message.function_call.name
        arguments = json.loads(message.function_call.arguments)

        if func_name in tools:
            result = tools[func_name]["func"](**arguments)
            log_tool_call(func_name, arguments, result)

            messages.append(message.to_dict())
            messages.append({
                "role": "function",
                "name": func_name,
                "content": result
            })

            # Segunda llamada
            second_response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            return second_response.choices[0].message.content
        else:
            return f"La función '{func_name}' no existe o no está disponible."
        
    else:
        return message.content
