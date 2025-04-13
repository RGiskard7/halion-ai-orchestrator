import streamlit as st
from app.core.env_manager import get_env_variables, set_env_variable, delete_env_variable, reload_env_variables

def render():
    """
    Renderiza la vista de gestión de variables de entorno
    """
    col1, col2 = st.columns([3,1])
    with col1:
        st.subheader("🔐 Gestión de Variables de Entorno")
    with col2:
        if st.button("🔄 Recargar Variables", help="Recarga las variables de entorno desde .env para uso inmediato"):
            with st.spinner("Recargando variables..."):
                reload_env_variables()
            st.success("✅ Variables recargadas exitosamente")
    
    # Variables Actuales
    render_existing_env_vars()
    
    # Nueva Variable
    render_new_env_var_form()

def render_existing_env_vars():
    """Renderiza la sección de variables de entorno existentes"""
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
                        reload_env_variables()  # Recargar para uso inmediato
                        st.success("✅ Variable actualizada")
                with col3:
                    if st.button("🗑️ Eliminar", key=f"delete_{key}"):
                        if delete_env_variable(key):
                            reload_env_variables()  # Recargar para actualizar la memoria
                            st.warning("Variable eliminada")
                            st.rerun()
    else:
        st.info("ℹ️ No hay variables de entorno configuradas")

def render_new_env_var_form():
    """Renderiza el formulario para añadir una nueva variable de entorno"""
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
                reload_env_variables()  # Recargar para uso inmediato
                st.success("✅ Variable añadida correctamente")
                st.rerun()
            else:
                st.error("❌ Nombre y valor son requeridos") 