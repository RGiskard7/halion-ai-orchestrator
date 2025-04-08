import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from executor import chat_with_tools
from logger import load_log_entries, clear_log_entries
from dynamic_tool_registry import register_tool, persist_tool_to_disk
from tool_manager import (
    load_all_tools, get_all_loaded_tools, get_loading_errors, 
    get_all_dynamic_tools, set_tool_status, get_tool_status, is_tool_active
)
from env_manager import get_env_variables, set_env_variable, delete_env_variable

# Configuración inicial
load_dotenv()
st.set_page_config(
    page_title="🧠 OpenAI Modular MCP",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (solo para botones y cajas)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización de estado
if "chat" not in st.session_state:
    st.session_state.chat = []
if "tools_loaded" not in st.session_state:
    st.session_state.tools_loaded = False

# == SIDEBAR ==
with st.sidebar:
    st.title("🧠 Control Panel")
    
    # Sección de Navegación Principal
    st.markdown("### 📍 Navegación")
    nav = st.radio(
        "Sección",  # Añadimos una etiqueta descriptiva
        options=["💬 Chat", "⚙️ Admin"],
        label_visibility="collapsed",  # La etiqueta seguirá oculta pero existe para accesibilidad
        key="navigation_radio"  # Añadimos una key única para mejor debugging
    )
    
    st.divider()
    
    # Sección de Configuración de IA
    st.markdown("### 🤖 Configuración IA")
    
    # API Key con mejor formato
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Tu clave API de OpenAI",
        placeholder="sk-..."
    )
    
    # Modelo y Temperatura en la misma sección
    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "Modelo",
            ["gpt-4", "gpt-3.5-turbo"],
            help="Selecciona el modelo de OpenAI"
        )
    with col2:
        temp = st.slider(
            "Temp.",
            0.0, 1.0, 0.7,
            help="Creatividad: 0=preciso, 1=creativo"
        )
    
    st.divider()
    
    # Sección de Herramientas
    st.markdown("### 🔧 Herramientas")
    
    # Status rápido de herramientas
    all_tools = {**get_all_loaded_tools(), **get_all_dynamic_tools()}
    active_tools = [name for name, _ in all_tools.items() if is_tool_active(name)]
    total_tools = len(all_tools)
    active_count = len(active_tools)
    
    # Mostrar resumen de estado
    st.markdown(f"**Estado**: {active_count}/{total_tools} activas")
    
    # Barra de progreso para visualización rápida
    if total_tools > 0:
        st.progress(active_count/total_tools, text="")
    
    # Lista expandible de herramientas activas
    with st.expander("Ver herramientas activas", expanded=False):
        if active_tools:
            for tool in sorted(active_tools):  # Ordenadas alfabéticamente
                st.markdown(f"✅ `{tool}`")
        else:
            st.info("ℹ️ No hay herramientas activas")
    
    st.divider()
    
    # Footer con información del sistema
    st.markdown(
        f"<div style='text-align: center; color: #888;'>"
        f"<small>Sistema MCP v1.0<br>"
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}</small>"
        f"</div>",
        unsafe_allow_html=True
    )

# == CHAT ==
if nav == "💬 Chat":
    st.title("💬 Asistente IA con Herramientas")
    
    # Mostrar mensajes del chat
    for msg in st.session_state.chat:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["bot"])

    # Input del usuario
    prompt = st.chat_input("¿En qué puedo ayudarte hoy?")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    reply = chat_with_tools(
                        prompt,
                        user_id="anon",
                        api_key=api_key,
                        model=model,
                        temperature=temp
                    )
                    st.markdown(reply)
                except Exception as e:
                    st.error(f"❌ Lo siento, ha ocurrido un error: {str(e)}")
                    reply = f"Error: {str(e)}"

        st.session_state.chat.append({"user": prompt, "bot": reply})

# == ADMIN ==
elif nav == "⚙️ Admin":
    st.title("⚙️ Panel de Administración")
    
    tabs = st.tabs(["🛠️ Herramientas", "🔐 Variables de Entorno", "📊 Logs"])
    
    # === TAB HERRAMIENTAS ===
    with tabs[0]:
        col1, col2 = st.columns([2,1])
        with col1:
            st.subheader("🔄 Gestión de Herramientas")
        with col2:
            if st.button("🔄 Recargar Herramientas", help="Recarga todas las herramientas desde el disco"):
                with st.spinner("Recargando herramientas..."):
                    load_all_tools()
                    st.session_state.tools_loaded = True
                st.success("✅ Herramientas recargadas exitosamente")
        
        # Herramientas Estáticas
        with st.expander("📁 Herramientas Estáticas", expanded=True):
            static_tools = get_all_loaded_tools()
            if static_tools:
                for k, v in static_tools.items():
                    col1, col2, col3 = st.columns([3,1,1])
                    with col1:
                        st.markdown(f"""
                        **`{k}`**  
                        {v['schema']['description']}  
                        {'🔄' if v['schema'].get('postprocess', True) else '📤'} {'_Post-procesado activo_' if v['schema'].get('postprocess', True) else '_Salida directa_'}
                        """)
                    with col2:
                        st.empty()  # Columna vacía para mantener el espaciado
                    with col3:
                        is_active = is_tool_active(k)
                        if st.toggle("Activa", value=is_active, key=f"toggle_{k}"):
                            if not is_active:  # Si estaba inactiva
                                set_tool_status(k, True)
                                st.success(f"✅ {k} activada")
                        else:
                            if is_active:  # Si estaba activa
                                set_tool_status(k, False)
                                st.warning(f"⚠️ {k} desactivada")
            else:
                st.info("ℹ️ No hay herramientas estáticas cargadas")
        
        # Herramientas Dinámicas
        with st.expander("💫 Herramientas Dinámicas", expanded=True):
            dynamic_tools = get_all_dynamic_tools()
            if dynamic_tools:
                for k, v in dynamic_tools.items():
                    col1, col2, col3 = st.columns([3,1,1])
                    with col1:
                        st.markdown(f"""
                        **`{k}`**  
                        {v['schema'].get('description', '(sin descripción)')}  
                        {'🔄' if v['schema'].get('postprocess', True) else '📤'} {'_Post-procesado activo_' if v['schema'].get('postprocess', True) else '_Salida directa_'}
                        """)
                    with col2:
                        st.empty()  # Columna vacía para mantener el espaciado
                    with col3:
                        is_active = is_tool_active(k)
                        if st.toggle("Activa", value=is_active, key=f"toggle_dyn_{k}"):
                            if not is_active:  # Si estaba inactiva
                                set_tool_status(k, True)
                                st.success(f"✅ {k} activada")
                        else:
                            if is_active:  # Si estaba activa
                                set_tool_status(k, False)
                                st.warning(f"⚠️ {k} desactivada")
            else:
                st.info("ℹ️ No hay herramientas dinámicas registradas")
        
        # Nueva Herramienta
        st.subheader("➕ Crear Nueva Herramienta")

        # Generación con IA
        with st.expander("🤖 Generar con IA", expanded=False):
            ai_prompt = st.text_area(
                "Describe la herramienta que necesitas",
                help="Describe en lenguaje natural qué quieres que haga la herramienta. Por ejemplo: 'Necesito una herramienta que traduzca texto a código morse y viceversa'",
                placeholder="Ejemplo: Una herramienta que calcule el IMC dado el peso en kg y la altura en metros..."
            )
            
            if st.button("🪄 Generar Herramienta", disabled=not ai_prompt):
                with st.spinner("La IA está generando tu herramienta..."):
                    try:
                        # Prompt para la IA
                        generation_prompt = f"""Genera una herramienta Python basada en esta descripción: '{ai_prompt}'

                        Debes proporcionar:
                        1. Nombre único y descriptivo para la herramienta
                        2. Descripción clara de su función
                        3. Schema JSON con los parámetros necesarios
                        4. Código Python que implemente la funcionalidad
                        5. Si debe usar post-procesado o no (true/false)

                        Responde en formato JSON exactamente así:
                        {{
                            "name": "nombre_herramienta",
                            "description": "Descripción clara",
                            "schema": {{
                                // El schema JSON completo
                            }},
                            "code": "// El código Python completo",
                            "postprocess": true/false
                        }}"""

                        # Llamada a la IA
                        response = chat_with_tools(
                            generation_prompt,
                            user_id="system",
                            api_key=api_key,
                            model="gpt-4",
                            temperature=0.7
                        )

                        # Parsear la respuesta
                        try:
                            tool_data = json.loads(response)
                            
                            # Rellenar el formulario con los datos generados
                            st.session_state.generated_name = tool_data["name"]
                            st.session_state.generated_desc = tool_data["description"]
                            st.session_state.generated_schema = json.dumps(tool_data["schema"], indent=2)
                            st.session_state.generated_code = tool_data["code"]
                            st.session_state.generated_postprocess = tool_data.get("postprocess", True)
                            
                            st.success("✨ Herramienta generada correctamente. Los campos del formulario se han rellenado automáticamente.")
                        except json.JSONDecodeError:
                            st.error("❌ La IA no generó un JSON válido. Por favor, intenta de nuevo.")
                    except Exception as e:
                        st.error(f"❌ Error al generar la herramienta: {str(e)}")

        st.divider()

        # Formulario de creación manual
        st.markdown("### ✏️ Crear Manualmente")
        with st.form("new_tool_form"):
            col1, col2, col3 = st.columns([2,2,1])
            with col1:
                name = st.text_input(
                    "Nombre",
                    value=st.session_state.get("generated_name", ""),
                    help="Nombre único para la herramienta"
                )
            with col2:
                desc = st.text_input(
                    "Descripción",
                    value=st.session_state.get("generated_desc", ""),
                    help="Breve descripción de su función"
                )
            with col3:
                postprocess = st.toggle(
                    "Post-procesado",
                    value=st.session_state.get("generated_postprocess", True),
                    help="Si está activado, la IA procesará el resultado. Si está desactivado, se mostrará el resultado directo de la herramienta."
                )
            
            json_schema = st.text_area(
                "Esquema JSON (parámetros)",
                height=150,
                value=st.session_state.get("generated_schema", """{
  "type": "object",
  "properties": {
    "param1": {
      "type": "string",
      "description": "Primer parámetro"
    }
  },
  "required": ["param1"]
}"""),
                help="Define los parámetros que acepta la herramienta"
            )
            
            code = st.text_area(
                "Código Python",
                height=200,
                value=st.session_state.get("generated_code", """def nueva_herramienta(param1):
    '''
    Documentación de la herramienta
    '''
    return f"Procesando: {param1}"
"""),
                help="Implementación de la herramienta"
            )
            
            if st.form_submit_button("✨ Crear Herramienta"):
                try:
                    with st.spinner("Registrando herramienta..."):
                        params = json.loads(json_schema)
                        schema = {
                            "name": name,
                            "description": desc,
                            "parameters": params,
                            "postprocess": postprocess
                        }
                        register_tool(name, schema, code)
                        persist_tool_to_disk(name, schema, code)
                    st.success(f"✅ Herramienta '{name}' creada exitosamente")
                    
                    # Limpiar los campos generados
                    for key in ["generated_name", "generated_desc", "generated_schema", "generated_code", "generated_postprocess"]:
                        if key in st.session_state:
                            del st.session_state[key]
                except Exception as e:
                    st.error(f"❌ Error al crear la herramienta: {str(e)}")
        
        # Errores de Carga
        with st.expander("🚨 Errores de Carga", expanded=False):
            errors = get_loading_errors()
            if errors:
                for e in errors:
                    st.error(f"📄 {e['file']}\n```\n{e['error']}\n```")
            else:
                st.success("✅ No se encontraron errores de carga")
    
    # === TAB VARIABLES DE ENTORNO ===
    with tabs[1]:
        st.subheader("🔐 Gestión de Variables de Entorno")
        
        # Variables Actuales
        envs = get_env_variables()
        if envs:
            st.markdown("### 📋 Variables Actuales")
            for key, val in envs.items():
                with st.expander(f"🔑 {key}", expanded=False):
                    col1, col2, col3 = st.columns([3,1,1])
                    with col1:
                        new_val = st.text_input(
                            "Valor",
                            value=val,
                            type="password" if "KEY" in key.upper() else "default",
                            key=f"edit_{key}"
                        )
                    with col2:
                        if st.button("💾 Guardar", key=f"save_{key}"):
                            set_env_variable(key, new_val)
                            st.success("✅ Variable actualizada")
                    with col3:
                        if st.button("🗑️ Eliminar", key=f"delete_{key}"):
                            if st.warning("¿Estás seguro?"):
                                delete_env_variable(key)
                                st.warning("Variable eliminada")
        else:
            st.info("ℹ️ No hay variables de entorno configuradas")
        
        # Nueva Variable
        st.markdown("### ➕ Nueva Variable")
        with st.form("new_env_var"):
            col1, col2 = st.columns(2)
            with col1:
                new_key = st.text_input("Nombre")
            with col2:
                new_value = st.text_input("Valor", type="password")
            
            if st.form_submit_button("✨ Añadir Variable"):
                if new_key.strip() and new_value.strip():
                    set_env_variable(new_key, new_value)
                    st.success("✅ Variable añadida correctamente")
                else:
                    st.error("❌ Nombre y valor son requeridos")
    
    # === TAB LOGS ===
    with tabs[2]:
        st.subheader("📊 Registro de Actividad")
        
        col1, col2 = st.columns([3,1])
        with col1:
            if st.button("📂 Cargar Registros"):
                with st.spinner("Cargando registros..."):
                    st.session_state.logs = load_log_entries()
                st.success("✅ Registros cargados")
        with col2:
            if st.button("🗑️ Limpiar Registros"):
                clear_log_entries()
                st.session_state.logs = []
                st.warning("🗑️ Registros eliminados")
        
        logs = st.session_state.get("logs", [])
        if logs:
            st.info(f"📝 {len(logs)} registros encontrados")
            
            # Botones de descarga
            col1, col2 = st.columns(2)
            with col1:
                json_data = json.dumps(logs, ensure_ascii=False, indent=2)
                st.download_button(
                    "📥 Descargar JSON",
                    data=json_data,
                    file_name=f"logs_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            with col2:
                df = pd.DataFrame(logs)
                st.download_button(
                    "📥 Descargar CSV",
                    data=df.to_csv(index=False),
                    file_name=f"logs_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            # Mostrar logs
            st.write("### 📋 Registros")
            for log in reversed(logs):
                with st.expander(f"⏱️ {log['timestamp']} - 🔧 {log['function']}"):
                    # Columna izquierda: Información básica
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.write("**Información Básica**")
                        st.write(f"**👤 Usuario:** {log.get('user_id', 'N/A')}")
                        st.write(f"**⏲️ Tiempo:** {log.get('execution_time', 'N/A')}s")
                    
                    # Columna derecha: Argumentos y Resultado
                    with col2:
                        st.write("**Detalles de Ejecución**")
                        if log.get('args'):
                            st.write("**⚙️ Argumentos:**")
                            st.json(log['args'])
                        st.write("**📝 Resultado:**")
                        st.code(log.get('result', 'N/A'))
        else:
            st.info("ℹ️ No hay registros cargados. Haz clic en 'Cargar Registros' para ver la actividad.")