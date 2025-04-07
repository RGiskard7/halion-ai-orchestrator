import streamlit as st
import os
import json
import pandas as pd

from dotenv import load_dotenv

from executor import chat_with_tools
from logger import load_log_entries, clear_log_entries
from dynamic_tool_registry import register_tool, persist_tool_to_disk
from tool_manager import load_all_tools, get_all_loaded_tools, get_loading_errors, get_all_dynamic_tools
from env_manager import get_env_variables, set_env_variable, delete_env_variable

load_dotenv()

st.set_page_config(page_title="🧠 OpenAI Modular Chat", layout="wide")

if "chat" not in st.session_state:
    st.session_state.chat = []

# == SIDEBAR ==
st.sidebar.title("⚙️ Configuración")
api_key = st.sidebar.text_input("🔑 API Key OpenAI", type="password", value=os.getenv("OPENAI_API_KEY", ""))
model = st.sidebar.selectbox("🧠 Modelo", ["gpt-4", "gpt-3.5-turbo"])
temp = st.sidebar.slider("🌡️ Temperatura", 0.0, 1.0, 0.7)

nav = st.sidebar.radio("Navegar a:", ["Chat", "Admin"])

# == CHAT ==
if nav == "Chat":
    st.title("🤖 Chat con Tools")
    for msg in st.session_state.chat:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["bot"])

    prompt = st.chat_input("Escribe tu mensaje...")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    reply = chat_with_tools(prompt,
                        user_id="anon",
                        api_key=api_key,
                        model=model,
                        temperature=temp
                    )
                except Exception as e:
                    reply = f"❌ Error: {str(e)}"
                st.markdown(reply)

        st.session_state.chat.append({"user": prompt, "bot": reply})

# == ADMIN ==
elif nav == "Admin":
    st.title("🛠️ Administración")
    st.subheader("Herramientas Cargadas")

    if st.button("🔄 Recargar Tools"):
        load_all_tools()
        st.success("Tools recargadas desde disco")

    st.write("**Tools de disco:**")
    static_tools = get_all_loaded_tools()
    if static_tools:
        for k, v in static_tools.items():
            st.markdown(f"- `{k}`: {v['schema']['description']}")
    else:
        st.info("No hay herramientas cargadas desde disco")

    st.write("**Tools en memoria (dinámicas):**")
    dynamic_tools = get_all_dynamic_tools()
    if dynamic_tools:
        for k, v in dynamic_tools.items():
            st.markdown(f"- `{k}`: {v['schema'].get('description', '(sin desc)')}")
    else:
        st.info("No hay herramientas dinámicas")

    # Registro de nueva tool
    st.subheader("➕ Crear nueva Tool dinámica")
    with st.form("new_tool_form"):
        name = st.text_input("Nombre de la tool")
        desc = st.text_input("Descripción")
        json_schema = st.text_area("Schema JSON (solo 'parameters')", "{\n  \"type\": \"object\",\n  \"properties\": {},\n  \"required\": []\n}")
        code = st.text_area("Código Python", height=200, value="def NUEVA_TOOL():\n    return \"Hola mundo\"")
        submit = st.form_submit_button("Crear")
        if submit:
            try:
                params = json.loads(json_schema)
                schema = {
                    "name": name,
                    "description": desc,
                    "parameters": params
                }
                register_tool(name, schema, code)
                persist_tool_to_disk(name, schema, code)
                st.success(f"La tool '{name}' se ha creado correctamente.")
            except Exception as e:
                st.error(f"Error al crear la tool: {e}")

    # Variables de entorno
    st.subheader("📋 Variables de entorno actuales")
    envs = get_env_variables()

    if not envs:
        st.info("No se han encontrado variables en el archivo .env")
    else:
        for key, val in envs.items():
            with st.expander(f"{key} = {val}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    new_val = st.text_input(f"Nuevo valor para {key}", value=val, key=f"edit_{key}")
                    if st.button(f"💾 Guardar {key}", key=f"save_{key}"):
                        set_env_variable(key, new_val)
                        st.success(f"Variable '{key}' actualizada.")
                with col2:
                    if st.button(f"🗑️ Eliminar {key}", key=f"delete_{key}"):
                        delete_env_variable(key)
                        st.warning(f"Variable '{key}' eliminada.")

    st.divider()

    # Añadir nueva variable
    st.subheader("➕ Añadir nueva variable")
    new_key = st.text_input("Nombre de la variable")
    new_value = st.text_input("Valor")

    if st.button("✅ Añadir"):
        if new_key.strip() == "" or new_value.strip() == "":
            st.error("Debes indicar nombre y valor.")
        else:
            set_env_variable(new_key, new_value)
            st.success(f"Variable '{new_key}' añadida o actualizada.")

    # Logs
    st.subheader("📋 Logs de Tools")
    if st.button("📂 Cargar logs"):
        st.session_state.logs = load_log_entries()
    logs = st.session_state.get("logs", [])
    if logs:
        st.success(f"{len(logs)} registros encontrados.")
        for log in reversed(logs):
            with st.expander(f"{log['timestamp']} - {log['function']}(...)", expanded=False):
                st.json(log)
    else:
        st.info("No hay logs cargados.")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("🗑 Borrar logs"):
            clear_log_entries()
            st.session_state.logs = []
            st.warning("Logs eliminados.")

    with col2:
        if logs:
            # Descargas
            json_data = json.dumps(logs, ensure_ascii=False, indent=2)
            st.download_button("Descargar JSON", data=json_data, file_name="logs.json", mime="application/json")
            df = pd.DataFrame(logs)
            st.download_button("Descargar CSV", data=df.to_csv(index=False), file_name="logs.csv", mime="text/csv")

    # Errores
    st.subheader("🚨 Errores de carga de Tools")
    errors = get_loading_errors()
    if errors:
        for e in errors:
            st.error(f"Archivo: {e['file']} => {e['error']}")
    else:
        st.success("No hay errores de carga.")