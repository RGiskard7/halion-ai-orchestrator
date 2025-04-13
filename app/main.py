import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Añadir directorio raíz al path de Python para los imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Definir directorio de la aplicación
APP_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(APP_DIR, "tools")
DEBUG_LOGS_DIR = os.path.join(APP_DIR, "debug_logs")

# Importar vistas
from app.views.chat_view import render as render_chat
from app.views.admin_view import render as render_admin

# Importar componentes principales del core
from app.core.tool_manager import load_all_tools, get_all_loaded_tools, get_all_dynamic_tools, is_tool_active

# Configuración inicial
def setup_app():
    # Cargar variables de entorno
    load_dotenv()
    
    # Configurar página de Streamlit
    st.set_page_config(
        page_title="🧠 OpenAI Modular MCP",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Estilos CSS personalizados
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
    
    # Inicializar el estado de la sesión si es necesario
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "tools_loaded" not in st.session_state:
        st.session_state.tools_loaded = False
        # Asegurar que las carpetas existen
        os.makedirs(TOOLS_DIR, exist_ok=True)
        os.makedirs(DEBUG_LOGS_DIR, exist_ok=True)
        # Cargar herramientas
        with st.spinner("Cargando herramientas..."):
            load_all_tools()
            st.session_state.tools_loaded = True
            # Imprimir información de herramientas cargadas para depuración
            print(f"Herramientas cargadas: {list(get_all_loaded_tools().keys())}")
            print(f"Herramientas dinámicas: {list(get_all_dynamic_tools().keys())}")
    
    # Actualizar el resumen de herramientas
    update_tool_summary()

def update_tool_summary():
    """Actualiza el resumen de herramientas en el estado de la sesión"""
    all_tools = {**get_all_loaded_tools(), **get_all_dynamic_tools()}
    active_tools = [name for name, _ in all_tools.items() if is_tool_active(name)]
    total_tools = len(all_tools)
    active_count = len(active_tools)
    
    st.session_state.tool_summary = {
        "all_tools": all_tools,
        "active_tools": active_tools,
        "total_tools": total_tools,
        "active_count": active_count
    }
    
    return st.session_state.tool_summary

def main():
    # Configuración inicial de la aplicación
    setup_app()
    
    # Sidebar para navegación
    with st.sidebar:
        st.markdown("### 📍 Navegación")
        nav = st.radio(
            "Sección",
            options=["💬 Chat", "⚙️ Admin"],
            label_visibility="collapsed",
            key="navigation_radio"
        )
        
        # Configuración de IA
        render_sidebar_config()
    
    # Renderizar la vista seleccionada
    if nav == "💬 Chat":
        render_chat()
    elif nav == "⚙️ Admin":
        render_admin()

def render_sidebar_config():
    """Renderiza la sección de configuración en la barra lateral"""
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
            ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4", "gpt-4o", "o1-mini"],
            help="Selecciona el modelo de OpenAI"
        )
    with col2:
        temp = st.slider(
            "Temp.",
            0.0, 1.0, 0.7,
            help="Creatividad: 0=preciso, 1=creativo"
        )
    
    # Expander para configuración avanzada
    with st.expander("⚙️ Configuración Avanzada", expanded=False):
        # max_tokens
        max_tokens = st.slider(
            "Max Tokens",
            100, 4000, 1024,
            help="Número máximo de tokens en la respuesta"
        )
        
        # top_p
        top_p = st.slider(
            "Top P",
            0.1, 1.0, 1.0,
            help="Controla la diversidad del texto (valores menores = más específico)"
        )
        
        # Columnas para presence y frequency penalty
        col1, col2 = st.columns(2)
        with col1:
            presence_penalty = st.slider(
                "Presence Penalty",
                -2.0, 2.0, 0.0,
                help="Penaliza nuevos temas (positivo = más diversos)"
            )
        with col2:
            frequency_penalty = st.slider(
                "Frequency Penalty",
                -2.0, 2.0, 0.0,
                help="Penaliza repeticiones (positivo = menos repetición)"
            )
        
        # Opciones adicionales
        seed = st.number_input(
            "Seed",
            min_value=-1,
            max_value=10000,
            value=-1,
            help="Semilla para reproducibilidad. -1 = desactivado"
        )
    
    # Guardar todas las configuraciones en el estado de sesión
    st.session_state.model_config = {
        "model": model,
        "temperature": temp,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "seed": None if seed == -1 else seed
    }
    
    # Sección de Herramientas
    render_sidebar_tools()

def render_sidebar_tools():
    """Renderiza la sección de herramientas en la barra lateral"""
    st.divider()
    
    # Sección de Herramientas
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 🔧 Herramientas")
    with col2:
        if st.button("🔄", key="reload_tools_sidebar", help="Recargar herramientas"):
            with st.spinner("Recargando..."):
                load_all_tools()
                update_tool_summary()
            st.success("✅")
            st.rerun()
    
    # Actualizar información de herramientas
    if "tool_summary" not in st.session_state:
        update_tool_summary()
    
    # Obtener datos del resumen
    tool_summary = st.session_state.tool_summary
    active_tools = tool_summary["active_tools"]
    total_tools = tool_summary["total_tools"]
    active_count = tool_summary["active_count"]
    
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

if __name__ == "__main__":
    main() 