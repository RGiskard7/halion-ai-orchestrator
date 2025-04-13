import streamlit as st
from typing import Dict, Any, Callable
import re

def render_tool_card(
    tool_name: str, 
    tool_info: Dict[str, Any], 
    is_active: bool, 
    on_view: Callable, 
    on_edit: Callable, 
    on_delete: Callable, 
    on_toggle: Callable,
    on_postprocess_toggle: Callable = None,  # Nueva función para manejar cambios de postprocess
    card_type: str = "static"  # Añadido para diferenciar entre static/dynamic
):
    """
    Renderiza una tarjeta para mostrar información de una herramienta
    
    Args:
        tool_name: Nombre de la herramienta
        tool_info: Diccionario con información de la herramienta
        is_active: Si la herramienta está activa o no
        on_view: Función a llamar cuando se presiona el botón de ver
        on_edit: Función a llamar cuando se presiona el botón de editar
        on_delete: Función a llamar cuando se presiona el botón de eliminar
        on_toggle: Función a llamar cuando se cambia el estado de activación
        on_postprocess_toggle: Función a llamar cuando se cambia el estado de postprocess
        card_type: Tipo de tarjeta ("static" o "dynamic") para diferenciación
    """
    # Sanitizar el nombre para usarlo como clave segura
    safe_key = re.sub(r'\W+', '_', tool_name).lower()
    
    # Obtener descripción y postprocess del schema
    schema = tool_info.get("schema", {})
    description = schema.get("description", "(sin descripción)")
    postprocess = schema.get("postprocess", True)
    
    # Utilizamos 6 columnas para añadir la columna de postprocess
    col1, col2, col3, col4, col5, col6 = st.columns([3, 0.5, 0.5, 0.5, 0.5, 0.5])
    
    with col1:
        st.markdown(f"""
            **`{tool_name}`**  
            {description}  
            {'🔄' if postprocess else '📤'} {'_Post-procesado activo_' if postprocess else '_Salida directa_'}
        """)
    
    with col2:
        # Botón para ver código - clave única para cada herramienta
        if st.button("👁️", key=f"view_{card_type}_{safe_key}", help=f"Ver código de {tool_name}"):
            on_view(tool_name)
    
    with col3:
        # Botón para editar
        if st.button("✏️", key=f"edit_{card_type}_{safe_key}", help=f"Editar {tool_name}"):
            on_edit(tool_name)
    
    with col4:
        # Botón para eliminar
        if st.button("🗑️", key=f"delete_{card_type}_{safe_key}", help=f"Eliminar {tool_name}"):
            on_delete(tool_name)
    
    with col5:
        # Toggle para activar/desactivar postprocess (si on_postprocess_toggle está definido)
        if on_postprocess_toggle:
            post_label = "🔄" if postprocess else "📤"
            if st.toggle(post_label, value=postprocess, key=f"postprocess_{card_type}_{safe_key}", 
                       help=f"{'Desactivar' if postprocess else 'Activar'} post-procesado para {tool_name}"):
                if not postprocess:  # Si estaba desactivado
                    on_postprocess_toggle(tool_name, True)
            else:
                if postprocess:  # Si estaba activado
                    on_postprocess_toggle(tool_name, False)
    
    with col6:
        # Toggle para activar/desactivar herramienta
        if st.toggle("✅", value=is_active, key=f"toggle_{card_type}_{safe_key}", 
                   help=f"{'Desactivar' if is_active else 'Activar'} herramienta {tool_name}"):
            if not is_active:  # Si estaba inactiva
                on_toggle(tool_name, True)
        else:
            if is_active:  # Si estaba activa
                on_toggle(tool_name, False) 