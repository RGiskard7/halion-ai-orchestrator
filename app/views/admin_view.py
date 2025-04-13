import streamlit as st
from app.views.tools_view import render as render_tools
from app.views.env_view import render as render_env
from app.views.logs_view import render as render_logs

def render():
    """
    Renderiza el panel de administración con pestañas para herramientas, 
    variables de entorno y logs
    """
    st.title("⚙️ Panel de Administración")
    
    tabs = st.tabs(["🛠️ Herramientas", "🔐 Variables de Entorno", "📊 Logs"])
    
    # Tab Herramientas
    with tabs[0]:
        render_tools()
    
    # Tab Variables de Entorno
    with tabs[1]:
        render_env()
    
    # Tab Logs
    with tabs[2]:
        render_logs() 