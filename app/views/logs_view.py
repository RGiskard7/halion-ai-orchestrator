import streamlit as st
import json
import pandas as pd
from datetime import datetime
from app.core.logger import load_log_entries, clear_log_entries

def render():
    """
    Renderiza la vista de logs
    """
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
        render_download_buttons(logs)
        
        # Mostrar logs
        render_logs_table(logs)
    else:
        st.info("ℹ️ No hay registros cargados. Haz clic en 'Cargar Registros' para ver la actividad.")

def render_download_buttons(logs):
    """Renderiza los botones para descargar los logs"""
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

def render_logs_table(logs):
    """Renderiza la tabla de logs"""
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