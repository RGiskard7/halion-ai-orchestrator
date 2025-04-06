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

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=messages,
        functions=function_schemas,
        function_call="auto"
    )

    message = response["choices"][0]["message"]

    if "function_call" in message:
        func_name = message["function_call"]["name"]
        arguments = json.loads(message["function_call"]["arguments"])

        if func_name in tools:
            result = tools[func_name]["func"](**arguments)
            log_tool_call(func_name, arguments, result)

            messages.append(message)
            messages.append({
                "role": "function",
                "name": func_name,
                "content": result
            })

            second_response = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=messages
            )

            return second_response["choices"][0]["message"]["content"]
        else:
            return f"No tienes permiso para usar la función '{func_name}'."
    else:
        return message["content"]
