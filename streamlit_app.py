import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import openai
import re
import time
import importlib

from executor import chat_with_tools
from logger import load_log_entries, clear_log_entries
from dynamic_tool_registry import register_tool, persist_tool_to_disk
from tool_manager import (
    load_all_tools, get_all_loaded_tools, get_loading_errors, 
    get_all_dynamic_tools, set_tool_status, get_tool_status, is_tool_active
)
from env_manager import get_env_variables, set_env_variable, delete_env_variable

def generate_tool_with_ai(description: str, api_key: str, model: str = "gpt-4", temperature: float = 0.7) -> str:
    """
    Genera código para una herramienta usando la API de OpenAI.
    
    Args:
        description: Descripción de la herramienta a generar
        api_key: API key de OpenAI
        model: Modelo a utilizar (por defecto "gpt-4")
        temperature: Temperatura para la generación (por defecto 0.7)
        
    Returns:
        str: Código Python de la herramienta generada
    
    Raises:
        ValueError: Si hay algún error en la generación
    """
    try:                
        # Verificar que tenemos una API key válida
        if not api_key:
            raise ValueError("No se proporcionó una API key válida")
            
        # Configurar cliente OpenAI
        client = openai.OpenAI(api_key=api_key)
        
        # Prompt simplificado para funciones/tools de OpenAI
        prompt = f"""
        Crea una herramienta Python con función y schema compatible con GPT (function calling). No des explicaciones, solo el código entre triple comillas.

            TAREA: Crear una herramienta Python para GPT function calling que cumpla con la siguiente descripción:
            {description}

            1. ESTRUCTURA OBLIGATORIA:
                - Función principal con nombre descriptivo en snake_case
                - Docstring detallado
                - Tipado de parámetros y retorno
                - Schema JSON que define la herramienta
                - Manejo de errores apropiado

            2. SCHEMA JSON REQUERIDO:
                - name: Nombre de la función (debe coincidir)
                - description: Descripción clara y concisa
                - postprocess: boolean (si el resultado necesita procesamiento por IA)
                - parameters: Definición JSON Schema de parámetros
                - required: Lista de parámetros obligatorios

            3. BUENAS PRÁCTICAS:
                - Código limpio y comentado
                - Validaciones de entrada
                - Mensajes de error descriptivos
                - Retorno de datos estructurados

            FORMATO:
            ```python
            from typing import Dict, Optional, Union
            import requests  # (si es necesario)

            def nombre_herramienta(param1: str, param2: Optional[int] = None) -> Dict[str, Union[str, int]]:
                \"\"\"
                Descripción detallada de la herramienta.
                
                Args:
                    param1 (str): Descripción del primer parámetro
                    param2 (int, optional): Descripción del segundo parámetro. Defaults to None.
                
                Returns:
                    Dict[str, Union[str, int]]: Descripción del formato de retorno
                    
                Raises:
                    ValueError: Descripción de cuándo se lanza este error
                \"\"\"
                # Validaciones
                if not param1:
                    raise ValueError("param1 no puede estar vacío")
                
                try:
                    # Lógica principal
                    return resultado
                except Exception as e:
                    raise Exception(f"Error en nombre_herramienta: {{e}}")

            schema = {{
                "name": "nombre_herramienta",
                "description": "Descripción concisa de la funcionalidad",
                "postprocess": true, # o False según necesidad
                "parameters": {{
                    "type": "object",
                    "properties": {{
                        "param1": {{
                            "type": "string",
                            "description": "Descripción detallada del parámetro"
                        }},
                        "param2": {{
                            "type": "integer",
                            "description": "Descripción detallada del parámetro opcional"
                        }}
                    }},
                    "required": ["param1"]
                }}
            }}
            ```
            IMPORTANTE:
            - La herramienta debe ser funcional y segura
            - Debe ser compatible las tools (antes funtion calling) de OpenAI
        """
        
        # Llamada a la API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto desarrollador de herramientas para GPT function calling."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        # Obtener el contenido de la respuesta
        content = response.choices[0].message.content
        if not content:
            raise ValueError("La respuesta no contiene contenido")
            
        # Extraer el código Python
        code_match = re.search(r"```python(.*?)```", content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Si no encuentra bloques específicos de Python, buscar cualquier bloque de código
        code_blocks = re.findall(r'```(.*?)```', content, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        
        # Si no hay bloques de código, usar todo el contenido
        return content.strip()
        
    except Exception as e:
        raise ValueError(f"Error al generar código: {str(e)}")

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
    
    # Guardar la API key en el estado de sesión
    if api_key:
        st.session_state.api_key = api_key
        # También la configuramos como variable de entorno para otras partes de la aplicación
        os.environ["OPENAI_API_KEY"] = api_key
    
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
        col1, col2 = st.columns([3,1])
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
                    col1, col2, col3, col4, col5 = st.columns([3,0.5,0.5,0.5,0.5])
                    with col1:
                        st.markdown(f"""
                        **`{k}`**  
                        {v['schema']['description']}  
                        {'🔄' if v['schema'].get('postprocess', True) else '📤'} {'_Post-procesado activo_' if v['schema'].get('postprocess', True) else '_Salida directa_'}
                        """)
                    with col2:
                        # Botón para ver código
                        if st.button("👁️", key=f"view_{k}", help=f"Ver código de {k}"):
                            # Guarda el nombre de la herramienta a ver en el estado
                            st.session_state.view_tool = k
                            st.session_state.view_tool_code = True
                    with col3:
                        # Botón para editar
                        if st.button("✏️", key=f"edit_{k}", help=f"Editar {k}"):
                            # Cargar contenido del archivo para edición
                            tool_path = os.path.join("tools", f"{k}.py")
                            try:
                                with open(tool_path, "r") as file:
                                    tool_code = file.read()
                                # Guardar en el estado para la edición
                                st.session_state.edit_tool = k
                                st.session_state.edit_tool_code = tool_code
                            except Exception as e:
                                st.error(f"No se pudo cargar el archivo: {str(e)}")
                    with col4:
                        # Botón para eliminar
                        if st.button("🗑️", key=f"delete_direct_{k}", help=f"Eliminar {k}"):
                            st.session_state.delete_tool = k
                            st.session_state.delete_tool_is_dynamic = False
                    with col5:
                        is_active = is_tool_active(k)
                        if st.toggle("Activa", value=is_active, key=f"toggle_{k}"):
                            if not is_active:  # Si estaba inactiva
                                set_tool_status(k, True)
                                st.success(f"✅ {k} activada")
                        else:
                            if is_active:  # Si estaba activa
                                set_tool_status(k, False)
                                st.warning(f"⚠️ {k} desactivada")
                
                # Modal para visualizar código
                if "view_tool" in st.session_state and "view_tool_code" in st.session_state and st.session_state.view_tool_code:
                    tool_name = st.session_state.view_tool
                    tool_path = os.path.join("tools", f"{tool_name}.py")
                    is_dynamic = st.session_state.get("view_tool_is_dynamic", False)
                    
                    st.info(f"📄 Visualizando código de `{tool_name}` ({'herramienta dinámica' if is_dynamic else 'herramienta estática'})")
                    try:
                        with open(tool_path, "r") as file:
                            tool_code = file.read()
                        st.code(tool_code, language="python")
                        
                        # Botones de acción
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✏️ Editar esta herramienta", key=f"edit_from_view_{tool_name}"):
                                st.session_state.edit_tool = tool_name
                                st.session_state.edit_tool_code = tool_code
                                st.session_state.edit_tool_is_dynamic = is_dynamic
                                st.session_state.view_tool_code = False
                        with col2:
                            if st.button("🗑️ Eliminar esta herramienta", key=f"delete_from_view_{tool_name}"):
                                st.session_state.delete_tool = tool_name
                                st.session_state.delete_tool_is_dynamic = is_dynamic
                                st.session_state.view_tool_code = False
                        
                        # Botón para cerrar
                        if st.button("❌ Cerrar", key="close_view"):
                            st.session_state.view_tool_code = False
                            if "view_tool_is_dynamic" in st.session_state:
                                del st.session_state.view_tool_is_dynamic
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al leer el código: {str(e)}")
                        if st.button("Cerrar", key="close_view_error"):
                            st.session_state.view_tool_code = False
                            if "view_tool_is_dynamic" in st.session_state:
                                del st.session_state.view_tool_is_dynamic
                            st.rerun()
                
                # Modal para editar código
                if "edit_tool" in st.session_state and "edit_tool_code" in st.session_state:
                    tool_name = st.session_state.edit_tool
                    is_dynamic = st.session_state.get("edit_tool_is_dynamic", False)
                    
                    st.warning(f"✏️ Editando herramienta `{tool_name}` ({'dinámica' if is_dynamic else 'estática'})")
                    
                    # Formulario de edición
                    with st.form(key=f"edit_form_{tool_name}"):
                        edited_code = st.text_area(
                            "Código de la herramienta", 
                            value=st.session_state.edit_tool_code,
                            height=400
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            save_button = st.form_submit_button("💾 Guardar cambios")
                        with col2:
                            cancel_button = st.form_submit_button("❌ Cancelar")
                    
                    # Procesar acciones del formulario
                    if save_button:
                        tool_path = os.path.join("tools", f"{tool_name}.py")
                        try:
                            # Guardar archivo
                            with open(tool_path, "w") as file:
                                file.write(edited_code)
                            
                            # Si es herramienta dinámica, también actualizar el registro
                            if is_dynamic:
                                try:
                                    # Extraer metadatos
                                    namespace = {}
                                    exec(edited_code, namespace)
                                    # Registrar de nuevo en el sistema
                                    if "schema" in namespace:
                                        register_tool(tool_name, namespace["schema"], edited_code)
                                    else:
                                        st.warning("No se encontró el schema en el código, la herramienta puede no funcionar correctamente")
                                except Exception as e:
                                    st.warning(f"Se guardó el archivo pero hubo un error al registrar la herramienta: {str(e)}")
                            
                            # Recargar herramientas
                            load_all_tools()
                            st.success(f"✅ Herramienta '{tool_name}' actualizada correctamente")
                            
                            # Limpiar estado
                            del st.session_state.edit_tool
                            del st.session_state.edit_tool_code
                            if "edit_tool_is_dynamic" in st.session_state:
                                del st.session_state.edit_tool_is_dynamic
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar cambios: {str(e)}")
                    
                    if cancel_button:
                        # Limpiar estado
                        del st.session_state.edit_tool
                        del st.session_state.edit_tool_code
                        if "edit_tool_is_dynamic" in st.session_state:
                            del st.session_state.edit_tool_is_dynamic
                        st.rerun()
                
                # Confirmación para eliminar
                if "delete_tool" in st.session_state:
                    tool_name = st.session_state.delete_tool
                    is_dynamic = st.session_state.get("delete_tool_is_dynamic", False)
                    
                    st.error(f"🗑️ ¿Estás seguro de que deseas eliminar la herramienta `{tool_name}`?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Sí, eliminar", key=f"confirm_delete_{tool_name}"):
                            tool_path = os.path.join("tools", f"{tool_name}.py")
                            try:
                                # Eliminar archivo
                                os.remove(tool_path)
                                # Marcar como inactiva
                                set_tool_status(tool_name, False)
                                # Recargar herramientas
                                load_all_tools()
                                st.success(f"✅ Herramienta '{tool_name}' eliminada correctamente")
                                
                                # Limpiar estado
                                del st.session_state.delete_tool
                                if "delete_tool_is_dynamic" in st.session_state:
                                    del st.session_state.delete_tool_is_dynamic
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al eliminar herramienta: {str(e)}")
                    with col2:
                        if st.button("❌ No, cancelar", key=f"cancel_delete_{tool_name}"):
                            # Limpiar estado
                            del st.session_state.delete_tool
                            if "delete_tool_is_dynamic" in st.session_state:
                                del st.session_state.delete_tool_is_dynamic
                            st.rerun()
            else:
                st.info("ℹ️ No hay herramientas estáticas cargadas")
        
        # Herramientas Dinámicas
        with st.expander("💫 Herramientas Dinámicas", expanded=True):
            dynamic_tools = get_all_dynamic_tools()
            if dynamic_tools:
                for k, v in dynamic_tools.items():
                    col1, col2, col3, col4, col5 = st.columns([3,0.5,0.5,0.5,0.5])
                    with col1:
                        st.markdown(f"""
                        **`{k}`**  
                        {v['schema'].get('description', '(sin descripción)')}  
                        {'🔄' if v['schema'].get('postprocess', True) else '📤'} {'_Post-procesado activo_' if v['schema'].get('postprocess', True) else '_Salida directa_'}
                        """)
                    with col2:
                        # Botón para ver código
                        if st.button("👁️", key=f"view_dyn_{k}", help=f"Ver código de {k}"):
                            # Guarda el nombre de la herramienta a ver en el estado
                            st.session_state.view_tool = k
                            st.session_state.view_tool_code = True
                            st.session_state.view_tool_is_dynamic = True
                    with col3:
                        # Botón para editar
                        if st.button("✏️", key=f"edit_dyn_{k}", help=f"Editar {k}"):
                            # Cargar contenido del archivo para edición
                            tool_path = os.path.join("tools", f"{k}.py")
                            try:
                                with open(tool_path, "r") as file:
                                    tool_code = file.read()
                                # Guardar en el estado para la edición
                                st.session_state.edit_tool = k
                                st.session_state.edit_tool_code = tool_code
                                st.session_state.edit_tool_is_dynamic = True
                            except Exception as e:
                                st.error(f"No se pudo cargar el archivo: {str(e)}")
                    with col4:
                        # Botón para eliminar
                        if st.button("🗑️", key=f"delete_direct_dyn_{k}", help=f"Eliminar {k}"):
                            st.session_state.delete_tool = k
                            st.session_state.delete_tool_is_dynamic = True
                    with col5:
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

        st.divider()
        
        # Nueva Herramienta
        st.subheader("➕ Crear Nueva Herramienta")

        # Generación con IA
        with st.expander("🤖 Generar con IA", expanded=False):
            ai_prompt = st.text_area(
                "Describe la herramienta que necesitas",
                help="Describe en lenguaje natural qué quieres que haga la herramienta. Por ejemplo: 'Necesito una herramienta que traduzca texto a código morse y viceversa'",
                placeholder="Ejemplo: Una herramienta que calcule el IMC dado el peso en kg y la altura en metros..."
            )
            
            # Botón para generar el código
            if st.button("🔍 Generar Código", disabled=not ai_prompt, key="generar_codigo"):
                with st.spinner("Generando código con IA..."):
                    try:
                        # Verificar API key
                        if not api_key:
                            st.error("No hay API Key configurada")
                            st.stop()
                            
                        # Generar código con la IA
                        code = generate_tool_with_ai(ai_prompt, api_key, model, temp)
                        
                        # Guardar el código generado en la sesión para usarlo después
                        st.session_state.codigo_generado = code
                        
                        # Extraer datos para mostrar información
                        try:
                            name, schema, _, _ = extract_code_and_schema(code)
                            st.session_state.tool_name = name
                            st.session_state.tool_schema = schema
                        except Exception as e:
                            st.warning(f"El código se generó pero hubo un problema al extraer metadatos: {str(e)}")
                            st.session_state.tool_name = "desconocido"
                            st.session_state.tool_schema = {"description": "No disponible"}
                        
                        # Mostrar el código generado
                        st.code(code, language="python")
                        
                        # Aquí mostramos el botón "Usar Esta Herramienta"
                        st.success("✅ Código generado correctamente. Revísalo y si te parece correcto, úsalo.")
                        
                        # Botón para reiniciar (opcional)
                        if st.button("🔄 Reiniciar", key="reiniciar_despues_crear"):
                            # Limpiar estado
                            if 'codigo_generado' in st.session_state:
                                del st.session_state.codigo_generado
                            if 'tool_name' in st.session_state:
                                del st.session_state.tool_name
                            if 'tool_schema' in st.session_state:
                                del st.session_state.tool_schema
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al generar código: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            
            # Mostrar el botón "Usar Esta Herramienta" solo si hay código generado
            if 'codigo_generado' in st.session_state:
                st.write("---")
                st.write(f"**Herramienta generada:** `{st.session_state.get('tool_name', 'Herramienta')}`")
                st.write(f"**Descripción:** {st.session_state.get('tool_schema', {}).get('description', 'No disponible')}")
                
                # Botón para usar la herramienta
                if st.button("✨ Usar Esta Herramienta", key="usar_herramienta"):
                    with st.spinner("Procesando y creando herramienta..."):
                        try:
                            # Extraer todos los datos necesarios
                            name, schema, code, func = extract_code_and_schema(st.session_state.codigo_generado)
                            
                            # Registrar y guardar la herramienta
                            register_tool(name, schema, code)
                            persist_tool_to_disk(name, schema, code)
                            set_tool_status(name, True)
                            
                            # Recargar todas las herramientas para actualizar la interfaz
                            load_all_tools()
                            
                            # Mensaje de éxito
                            st.success(f"✅ Herramienta '{name}' creada y activada exitosamente")
                            
                            # Limpiar estado
                            if 'codigo_generado' in st.session_state:
                                del st.session_state.codigo_generado
                            if 'tool_name' in st.session_state:
                                del st.session_state.tool_name
                            if 'tool_schema' in st.session_state:
                                del st.session_state.tool_schema
                            
                            # Recargar la página para mostrar la herramienta en las listas
                            st.rerun()
                                
                        except Exception as e:
                            st.error(f"❌ Error al crear la herramienta: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())

        with st.expander("✏️ Crear Manualmente", expanded=False):
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
                            
                            # Recargar todas las herramientas para actualizar la interfaz
                            load_all_tools()
                        
                        st.success(f"✅ Herramienta '{name}' creada exitosamente")
                        
                        # Limpiar los campos generados
                        for key in ["generated_name", "generated_desc", "generated_schema", "generated_code", "generated_postprocess"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                        # Recargar la página para mostrar la herramienta en las listas
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al crear la herramienta: {str(e)}")

        st.divider()
        
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