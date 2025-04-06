from fastapi import FastAPI, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from auth import manager, load_user, fake_users_db
from executor import chat_with_tools
from logger import load_log_entries
from tool_manager import get_all_loaded_tools, get_loading_errors, load_all_tools
from dynamic_tool_registry import get_all_dynamic_tools, register_tool, persist_tool_to_disk
from passlib.hash import bcrypt
import json
import os
import yaml

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        user = await manager.get_current_user(request)
        return templates.TemplateResponse("chat.html", {"request": request, "chat": [], "user": user})
    except Exception:
        # Usuario no autenticado → mostrar login
        return templates.TemplateResponse("chat.html", {"request": request, "chat": [], "user": None})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = load_user(username)
    if not user or not bcrypt.verify(password, user["password"]):
        return templates.TemplateResponse("chat.html", {"request": request, "error": "Credenciales incorrectas"})

    resp = RedirectResponse(url="/", status_code=302)
    manager.set_cookie(resp, username)
    return resp

@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie(manager.cookie_name)
    return resp

@app.post("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request, prompt: str = Form(...), user=Depends(manager)):
    response = await chat_with_tools(prompt, user_id=user)
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "chat": [{"user": prompt, "bot": response}],
        "user": user
    })

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, user=Depends(manager), msg: str = Query(default=None)):
    if user["name"] != "Edu":
        return RedirectResponse(url="/", status_code=302)

    users = fake_users_db
    logs = load_log_entries(limit=50)
    tools = get_all_dynamic_tools()
    static_tools = get_all_loaded_tools()
    errors = get_loading_errors()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "users": users,
        "logs": logs,
        "tools": tools,
        "static_tools": static_tools,
        "errors": errors,
        "msg": msg
    })

@app.post("/admin/create-user")
def create_user(username: str = Form(...), password: str = Form(...), tools: str = Form(...), user=Depends(manager)):
    if user["name"] != "Edu":
        raise HTTPException(status_code=403)
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    from passlib.hash import bcrypt
    fake_users_db[username] = {
        "name": username,
        "password": bcrypt.hash(password),
        "tools": [t.strip() for t in tools.split(",") if t.strip()]
    }
    return RedirectResponse(url="/admin?msg=Usuario+creado", status_code=302)

@app.post("/admin/delete-user")
def delete_user(username: str = Form(...), user=Depends(manager)):
    if user["name"] != "Edu":
        raise HTTPException(status_code=403)
    if username != "edu" and username in fake_users_db:
        del fake_users_db[username]
    return RedirectResponse(url="/admin?msg=Usuario+eliminado", status_code=302)

@app.get("/admin/reload-tools")
def reload_tools(user=Depends(manager)):
    if user["name"] != "Edu":
        raise HTTPException(status_code=403)
    load_all_tools()
    return RedirectResponse(url="/admin?msg=Tools+recargadas", status_code=302)

@app.post("/admin/create-tool")
def create_tool(name: str = Form(...), description: str = Form(...), json_schema: str = Form(...), func_code: str = Form(...), user=Depends(manager)):
    if user["name"] != "Edu":
        raise HTTPException(status_code=403)
    schema = {
        "name": name,
        "description": description,
        "parameters": json.loads(json_schema)
    }
    try:
        register_tool(name, schema, func_code)
        persist_tool_to_disk(name, schema, func_code)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=400)
    return RedirectResponse(url="/admin?msg=Tool+guardada+correctamente", status_code=302)

@app.post("/admin/delete-tool")
def delete_tool(name: str = Form(...), user=Depends(manager)):
    if user["name"] != "Edu":
        raise HTTPException(status_code=403)
    path = os.path.join("tools", f"{name}.py")
    if os.path.exists(path):
        os.remove(path)
        return RedirectResponse(url="/admin?msg=Tool+eliminada", status_code=302)
    return RedirectResponse(url="/admin?msg=Tool+no+encontrada", status_code=302)

@app.get("/admin/edit-tool", response_class=HTMLResponse)
def edit_tool(name: str, request: Request, user=Depends(manager)):
    if user["name"] != "Edu":
        raise HTTPException(status_code=403)

    path = os.path.join("tools", f"{name}.py")
    if not os.path.exists(path):
        return RedirectResponse("/admin?msg=Tool+no+encontrada", status_code=302)

    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    schema_file = os.path.join("tools", f"{name}.yaml")
    schema = ""
    if os.path.exists(schema_file):
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = yaml.safe_load(f)
            schema = json.dumps(schema, indent=2)

    return templates.TemplateResponse("edit_tool.html", {
        "request": request,
        "name": name,
        "code": code,
        "schema": schema
    })

@app.post("/admin/update-tool")
def update_tool(name: str = Form(...), json_schema: str = Form(...), func_code: str = Form(...), user=Depends(manager)):
    if user["name"] != "Edu":
        raise HTTPException(status_code=403)
    try:
        ns = {}
        exec(func_code, ns)
        if name not in ns:
            raise Exception("La función no se llama igual que el archivo")
        schema = json.loads(json_schema)

        with open(os.path.join("tools", f"{name}.py"), "w", encoding="utf-8") as f:
            f.write(func_code.strip() + "\n\n")
            f.write("schema = ")
            f.write(json.dumps(schema, indent=2))

        with open(os.path.join("tools", f"{name}.yaml"), "w", encoding="utf-8") as f:
            yaml.dump(schema, f, allow_unicode=True)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1><p><a href='/admin'>Volver</a></p>", status_code=400)

    return RedirectResponse(f"/admin?msg=Tool+{name}+actualizada", status_code=302)
