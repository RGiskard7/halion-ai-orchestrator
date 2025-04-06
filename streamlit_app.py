import streamlit as st
import os
import json
from executor import chat_with_tools
from tool_manager import load_all_tools, get_all_loaded_tools, get_loading_errors
from dynamic_tool_registry import get_all_dynamic_tools, register_tool, persist_tool_to_disk
from logger import load_log_entries
import yaml

# 1) Carga (o recarga) las tools al iniciar
if "tools_loaded" not in st.session_state:
    load_all_tools()
    st.session_state["tools_loaded"] = True

st.title("OpenAI Modular MCP — MVP con Streamlit")

# 2) Definimos secciones con st.tabs
tab_chat, tab_admin = st.tabs(["Chat", "Tools Admin"])

############################################################
# CHAT TAB
############################################################
with tab_chat:
    st.header("Chat con GPT + Tools")

    prompt = st.text_input("Escribe tu mensaje:", "")
    if st.button("Enviar"):
        if prompt.strip():
            # Llamada async -> en Streamlit haremos sync
            import asyncio
            response = asyncio.run(chat_with_tools(prompt, user_id="anon"))
            st.write(f"**Tú**: {prompt}")
            st.write(f"**IA**: {response}")

############################################################
# ADMIN TAB
############################################################
with tab_admin:
    st.header("Panel de administración de Tools")

    # a) Recargar Tools
    if st.button("🔄 Recargar Tools desde disco"):
        load_all_tools()
        st.success("Tools recargadas.")

    # b) Mostrar Tools cargadas (disco)
    st.subheader("Tools cargadas desde disco")
    static_tools = get_all_loaded_tools()
    for name, info in static_tools.items():
        st.write(f"**{name}** — {info['schema'].get('description','(sin desc)')}")

    # c) Tools dinámicas (memoria)
    st.subheader("Tools dinámicas (memoria)")
    dynamic_tools = get_all_dynamic_tools()
    for name, info in dynamic_tools.items():
        st.write(f"**{name}** — {info['schema'].get('description','(sin desc)')}")

    # d) Crear nueva Tool
    st.subheader("Crear nueva Tool")
    new_name = st.text_input("Nombre de la tool")
    new_desc = st.text_input("Descripción breve")
    new_json_schema = st.text_area("JSON Schema", value='{\n  "type": "object",\n  "properties": {},\n  "required": []\n}')
    new_code = st.text_area("Código Python", height=150, value='''def NOMBRE():
    return "Hola Mundo"''')

    if st.button("Registrar nueva Tool"):
        try:
            params = json.loads(new_json_schema)
            schema = {
                "name": new_name,
                "description": new_desc,
                "parameters": params
            }
            register_tool(new_name, schema, new_code)
            persist_tool_to_disk(new_name, schema, new_code)
            st.success(f"Tool '{new_name}' guardada correctamente.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # e) Errores de carga
    st.subheader("Errores de carga")
    errors = get_loading_errors()
    if errors:
        for err in errors:
            st.error(f"Archivo {err['file']}: {err['error']}")
    else:
        st.info("No hay errores de carga.")

    # f) Logs
    st.subheader("Últimos logs")
    logs = load_log_entries(limit=50)
    if logs:
        for log in logs:
            st.write(f"**{log['timestamp']}** → {log['function']}({log['arguments']}) = {log['result']}")
    else:
        st.info("Aún no hay logs.")
