from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from executor import chat_with_tools
from logger import load_log_entries
from tool_manager import get_all_loaded_tools, get_loading_errors, load_all_tools
from dynamic_tool_registry import get_all_dynamic_tools, register_tool, persist_tool_to_disk

import json
import os
import yaml

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Modo anónimo: no hay login
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "chat": [],
        "user": {"name": "anon"}
    })


@app.post("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request, prompt: str = Form(...)):
    # Llamamos a GPT con user_id="anon"
    response = await chat_with_tools(prompt, user_id="anon")
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "chat": [{"user": prompt, "bot": response}],
        "user": {"name": "anon"}
    })


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, msg: str = Query(default=None)):
    # No hay usuarios de verdad, simulamos uno
    users = {
        "anon": {
            "name": "anon",
            "tools": []
        }
    }
    logs = load_log_entries(limit=50)
    tools = get_all_dynamic_tools()
    static_tools = get_all_loaded_tools()
    errors = get_loading_errors()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": {"name": "anon"},
        "users": users,
        "logs": logs,
        "tools": tools,
        "static_tools": static_tools,
        "errors": errors,
        "msg": msg
    })


@app.post("/admin/create-tool")
def create_tool(
    name: str = Form(...),
    description: str = Form(...),
    json_schema: str = Form(...),
    func_code: str = Form(...),
):
    # Convertimos el JSON del schema
    try:
        parameters = json.loads(json_schema)
    except json.JSONDecodeError as e:
        return HTMLResponse(f"<h1>JSON inválido: {e}</h1><a href='/admin'>Volver</a>", status_code=400)

    schema = {
        "name": name,
        "description": description,
        "parameters": parameters
    }
    try:
        # Registramos y persistimos en disco
        register_tool(name, schema, func_code)
        persist_tool_to_disk(name, schema, func_code)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=400)

    return RedirectResponse(url="/admin?msg=Tool+guardada+correctamente", status_code=302)


@app.post("/admin/delete-tool")
def delete_tool(name: str = Form(...)):
    path = os.path.join("tools", f"{name}.py")
    if os.path.exists(path):
        os.remove(path)
        return RedirectResponse(url="/admin?msg=Tool+eliminada", status_code=302)
    return RedirectResponse(url="/admin?msg=Tool+no+encontrada", status_code=302)


@app.get("/admin/edit-tool", response_class=HTMLResponse)
def edit_tool(name: str, request: Request):
    path = os.path.join("tools", f"{name}.py")
    if not os.path.exists(path):
        return RedirectResponse("/admin?msg=Tool+no+encontrada", status_code=302)

    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    schema_file = os.path.join("tools", f"{name}.yaml")
    schema = ""
    if os.path.exists(schema_file):
        with open(schema_file, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
            schema = json.dumps(loaded, indent=2)

    return templates.TemplateResponse("edit_tool.html", {
        "request": request,
        "name": name,
        "code": code,
        "schema": schema
    })


@app.post("/admin/update-tool")
def update_tool(name: str = Form(...), json_schema: str = Form(...), func_code: str = Form(...)):
    try:
        ns = {}
        exec(func_code, ns)
        if name not in ns:
            raise Exception("La función no se llama igual que el archivo")

        new_schema = json.loads(json_schema)

        # Sobrescribimos el archivo .py
        py_path = os.path.join("tools", f"{name}.py")
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(func_code.strip() + "\n\n")
            f.write("schema = ")
            f.write(json.dumps(new_schema, indent=2))

        # Guardar .yaml
        yaml_path = os.path.join("tools", f"{name}.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(new_schema, f, allow_unicode=True)

    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1><p><a href='/admin'>Volver</a></p>", status_code=400)

    return RedirectResponse(f"/admin?msg=Tool+{name}+actualizada", status_code=302)


@app.get("/admin/reload-tools")
def reload_tools():
    load_all_tools()
    return RedirectResponse(url="/admin?msg=Tools+recargadas", status_code=302)
