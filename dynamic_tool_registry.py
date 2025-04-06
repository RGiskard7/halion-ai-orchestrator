import os
import json

TOOLS_FOLDER = "tools"
dynamic_tools = {}

def register_tool(name: str, schema: dict, func_code: str):
    namespace = {}
    exec(func_code, namespace)

    if name not in namespace:
        raise ValueError(f"La función '{name}' no está definida en el código")

    dynamic_tools[name] = {
        "schema": schema,
        "func": namespace[name],
        "code": func_code
    }

def get_all_dynamic_tools():
    return dynamic_tools

def get_dynamic_tool(name):
    return dynamic_tools.get(name)

def persist_tool_to_disk(name: str, schema: dict, func_code: str):
    os.makedirs(TOOLS_FOLDER, exist_ok=True)
    path = os.path.join(TOOLS_FOLDER, f"{name}.py")

    with open(path, "w", encoding="utf-8") as f:
        f.write(func_code.strip() + "\n\n")
        f.write("schema = ")
        json_schema = json.dumps(schema, indent=2, ensure_ascii=False)
        f.write(json_schema + "\n")
