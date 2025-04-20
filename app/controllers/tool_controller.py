import os
import streamlit as st
import time
import traceback
from app.core.tool_manager import (
    load_all_tools, get_all_loaded_tools, get_all_dynamic_tools, 
    set_tool_status, is_tool_active, get_loading_errors,
    set_tool_postprocess, get_tool_postprocess
)
from app.core.tool_definition_registry import (
    register_tool, persist_tool_to_disk, get_tool_code, save_tool_code, delete_tool_file,
    get_all_dynamic_tools as core_get_all_dynamic_tools,
    TOOLS_FOLDER
)
from app.services import tool_service

# Ya no definimos TOOLS_FOLDER aquí, lo importamos directamente de dynamic_tool_registry
# para asegurar consistencia en las rutas

# Asegurarse de que el directorio tools existe
os.makedirs(TOOLS_FOLDER, exist_ok=True)

def reload_tools():
    """
    Recarga todas las herramientas disponibles
    
    Returns:
        bool: True si la operación fue exitosa
    """
    try:
        # Cargar herramientas
        load_all_tools()
        # Actualizar el resumen de herramientas en la sesión
        update_tool_summary()
        return True
    except Exception as e:
        st.error(f"Error al recargar herramientas: {str(e)}")
        return False

def update_tool_summary():
    """
    Actualiza el resumen de herramientas en el estado de la sesión
    
    Returns:
        dict: Resumen actualizado de herramientas
    """
    # Status rápido de herramientas
    all_tools = {**get_all_loaded_tools(), **get_all_dynamic_tools()}
    active_tools = [name for name, _ in all_tools.items() if is_tool_active(name)]
    total_tools = len(all_tools)
    active_count = len(active_tools)
    
    # Actualizar en el estado de sesión
    st.session_state.tool_summary = {
        "all_tools": all_tools,
        "active_tools": active_tools,
        "total_tools": total_tools,
        "active_count": active_count
    }
    
    return st.session_state.tool_summary

def handle_tool_view(tool_name):
    """
    Maneja la acción de ver una herramienta
    
    Args:
        tool_name: Nombre de la herramienta a ver
    """
    # Determinar si es dinámica o estática
    is_dynamic = tool_name in get_all_dynamic_tools()
    
    # Guardar estado para mostrar el código
    st.session_state.view_tool = tool_name
    st.session_state.view_tool_code = True
    st.session_state.view_tool_is_dynamic = is_dynamic

def handle_tool_edit(tool_name):
    """
    Maneja la acción de editar una herramienta
    
    Args:
        tool_name: Nombre de la herramienta a editar
    """
    # Determinar si es dinámica o estática
    is_dynamic = tool_name in get_all_dynamic_tools()
    
    # Obtener código desde el core
    tool_code = get_tool_code(tool_name)
    try:
        if tool_code is not None:
            st.session_state.edit_tool = tool_name
            st.session_state.edit_tool_code = tool_code
            st.session_state.edit_tool_is_dynamic = is_dynamic
        else:
            st.error(f"No se pudo obtener el código para la herramienta '{tool_name}'.")
    except Exception as e:
        st.error(f"Error al preparar la edición de '{tool_name}': {e}")

def handle_tool_delete(tool_name):
    """
    Maneja la acción de eliminar una herramienta
    
    Args:
        tool_name: Nombre de la herramienta a eliminar
    """
    # Determinar si es dinámica o estática
    is_dynamic = tool_name in get_all_dynamic_tools()
    
    # Guardar estado para mostrar confirmación
    st.session_state.delete_tool = tool_name
    st.session_state.delete_tool_is_dynamic = is_dynamic

def handle_tool_toggle(tool_name, active):
    """
    Maneja la acción de activar/desactivar una herramienta
    
    Args:
        tool_name: Nombre de la herramienta a activar/desactivar
        active: True para activar, False para desactivar
    """
    # Cambiar estado
    set_tool_status(tool_name, active)
    
    # Actualizar resumen
    update_tool_summary()
    
    # Mostrar mensaje
    if active:
        st.success(f"✅ {tool_name} activada")
    else:
        st.warning(f"⚠️ {tool_name} desactivada")
    
    # Pequeña pausa para mostrar el mensaje
    time.sleep(0.3)
    
    # Recargar para aplicar cambios
    st.rerun()

def save_tool_edit(tool_name, edited_code, is_dynamic=False):
    """
    Guarda los cambios de edición de una herramienta llamando al core.
    
    Args:
        tool_name: Nombre de la herramienta
        edited_code: Código editado
        is_dynamic: Si es una herramienta dinámica
        
    Returns:
        bool: True si la operación fue exitosa
    """
    # Guardar archivo a través del core
    if not save_tool_code(tool_name, edited_code):
        st.error(f"Error al guardar el archivo para '{tool_name}'")
        return False

    # Si es herramienta dinámica, re-registrarla para actualizar la función/schema en memoria
    if is_dynamic:
        try:
            # El registro interno maneja exec y extracción de schema/func
            namespace = {}
            exec(edited_code, namespace)
            # Usar el nombre del schema guardado, no el original por si cambió
            schema_name = namespace["schema"].get("name", tool_name)
            register_tool(tool_name, namespace["schema"], edited_code)
            if schema_name != tool_name:
                st.warning(f"El nombre en el schema ({schema_name}) no coincide con el nombre del archivo ({tool_name}). Se usará el nombre del schema.")
        except Exception as e:
            st.warning(f"Archivo guardado, pero hubo un error al re-registrar la herramienta dinámica '{tool_name}': {str(e)}")

    # Recargar herramientas para asegurar consistencia general
    load_all_tools()
    update_tool_summary()

    return True

def confirm_tool_delete(tool_name):
    """
    Confirma y ejecuta la eliminación de una herramienta
    
    Args:
        tool_name: Nombre de la herramienta a eliminar
        
    Returns:
        bool: True si la operación fue exitosa
    """
    # Eliminar archivo a través del core
    if not delete_tool_file(tool_name):
        st.warning(f"No se pudo eliminar el archivo para '{tool_name}' (quizás ya estaba borrado).", icon="⚠️")
    # Marcar como inactiva
    set_tool_status(tool_name, False)
    # Recargar herramientas
    load_all_tools()
    update_tool_summary()
    
    return True

def _create_and_persist_tool(name, schema, code):
    """
    Registra en memoria, persiste a disco y recarga. NO maneja env vars.
    
    Args:
        name: Nombre de la herramienta (puede no ser correcto)
        schema: Schema JSON de la herramienta
        code: Código de la herramienta
        
    Returns:
        bool: True si la operación fue exitosa
    """
    try:
        # Obtener el nombre correcto del schema
        tool_name = schema.get("name", name)
        
        # Intentar registrar en memoria primero (valida el código)
        try:
            registered_name = register_tool(tool_name, schema, code)
        except Exception as reg_e:
            st.error(f"Error al registrar la herramienta en memoria: {reg_e}")
            return False
        
        # Guardar archivo en disco
        success = persist_tool_to_disk(registered_name, schema, code)
        
        if not success:
            # Considerar revertir el registro en memoria si falla la persistencia?
            st.error(f"Error al guardar el archivo para la herramienta '{registered_name}'. Ver logs para detalles.")
            return False
        
        # Activar la herramienta
        set_tool_status(registered_name, True)
        
        # Recargar herramientas
        load_all_tools()
        
        # Actualizar el resumen de herramientas
        update_tool_summary()
        
        return True
    except Exception as e:
        st.error(f"Error al crear la herramienta: {str(e)}")
        # Loggear el traceback completo para diagnóstico
        print(f"[Controller Error] Traceback al crear tool: {traceback.format_exc()}")
        return False

def handle_tool_postprocess_toggle(tool_name, postprocess_active):
    """
    Maneja la acción de activar/desactivar el postprocess de una herramienta
    
    Args:
        tool_name: Nombre de la herramienta a modificar
        postprocess_active: True para activar postprocess, False para desactivarlo
    """
    # Usar la nueva función del tool_manager para cambiar el estado
    try:
        set_tool_postprocess(tool_name, postprocess_active)
        # Actualizar el resumen para reflejar el cambio si afecta a get_tools()
        update_tool_summary()

        # Mostrar mensaje (¿Debería estar en la vista? Por ahora aquí)
        if postprocess_active:
            st.success(f"✅ Postprocess activado para {tool_name}")
        else:
            st.warning(f"⚠️ Postprocess desactivado para {tool_name}")

        # Pequeña pausa y rerun (¿Debería estar en la vista? Por ahora aquí)
        time.sleep(0.3)
        st.rerun()

    except Exception as e:
        st.error(f"Error al cambiar el estado de postprocess para '{tool_name}': {str(e)}")
        import traceback
        print(f"[Controller Error] Traceback al cambiar postprocess: {traceback.format_exc()}")

def handle_create_manual_tool(name: str, schema: dict, code: str):
    """Maneja la creación de una tool definida manualmente por el usuario."""
    return _create_and_persist_tool(name, schema, code)

def handle_create_generated_tool(tool_name: str, schema: dict, code: str, env_vars_with_values: list[dict]):
    """Maneja la creación de una tool generada por IA, incluyendo guardado de env vars."""
    try:
        # 1. Guardar variables de entorno detectadas (y posiblemente modificadas por el usuario)
        if env_vars_with_values:
            with st.spinner("Guardando variables de entorno detectadas..."):
                saved_vars, unchanged_vars = tool_service.save_detected_env_vars(env_vars_with_values)
            if saved_vars:
                st.success(f"✅ Variables guardadas/actualizadas en .env: {', '.join(saved_vars)}")
            if unchanged_vars:
                st.info(f"ℹ️ Variables existentes sin cambios: {', '.join(unchanged_vars)}")
            # Considerar mostrar error si save_detected_env_vars falla?

        # 2. Crear y persistir la herramienta
        with st.spinner(f"Creando y guardando herramienta '{tool_name}'..."):
            success = _create_and_persist_tool(tool_name, schema, code)

        if success:
            st.success(f"✅ Herramienta '{tool_name}' creada y activada exitosamente.")
            # Limpiar estado de generación AI en la sesión
            if "ai_prompt" in st.session_state: st.session_state.ai_prompt = ""
            if "generated_code" in st.session_state: del st.session_state.generated_code
            if "generated_tool_name" in st.session_state: del st.session_state.generated_tool_name
            if "generated_schema" in st.session_state: del st.session_state.generated_schema
            if "generated_env_vars" in st.session_state: del st.session_state.generated_env_vars
            if "generation_error" in st.session_state: del st.session_state.generation_error
            return True
        else:
            # El error específico ya se mostró en _create_and_persist_tool
            return False

    except Exception as e:
        st.error(f"Error general al procesar la herramienta generada: {e}")
        import traceback
        print(f"[Controller Error] Traceback al crear tool generada: {traceback.format_exc()}")
        return False

def handle_generate_tool_ai(description: str):
    """
    Orquesta la generación de código de tool con IA y la extracción de metadatos/env vars.
    Actualiza st.session_state con los resultados o errores.
    """
    # Limpiar estado previo
    st.session_state.generated_code = None
    st.session_state.generated_tool_name = None
    st.session_state.generated_schema = None
    st.session_state.generated_env_vars = None
    st.session_state.generation_error = None

    try:
        api_key = st.session_state.get("api_key")
        model_config = st.session_state.get("model_config")
        if not api_key:
            st.error("❌ Falta la API Key de OpenAI en la configuración.")
            st.session_state.generation_error = "API Key no configurada."
            return

        # Llamar al servicio para generar código
        generated_code = tool_service.generate_tool_code_via_ai(description, api_key, model_config)
        st.session_state.generated_code = generated_code

        # Llamar al servicio para extraer metadatos y env vars
        tool_name, schema, env_vars = tool_service.extract_tool_metadata_and_env_vars(generated_code)

        if tool_name:
            st.session_state.generated_tool_name = tool_name
        if schema:
            st.session_state.generated_schema = schema
        if env_vars is not None: # Puede ser lista vacía
            st.session_state.generated_env_vars = env_vars

        if not tool_name or not schema:
            st.warning("⚠️ No se pudieron extraer completamente el nombre o el schema del código generado.")
            # No poner error aquí, permitir al usuario usarlo igualmente si quiere

    except Exception as e:
        st.error(f"❌ Error durante la generación o análisis: {e}")
        st.session_state.generation_error = str(e)

# --- Funciones para que la Vista obtenga datos --- #

def get_static_tools_view() -> dict:
    """Devuelve las herramientas estáticas cargadas."""
    # Directamente desde tool_manager por ahora, ya que no hay lógica adicional aquí.
    return get_all_loaded_tools()

def get_dynamic_tools_view() -> dict:
    """Devuelve las herramientas dinámicas registradas."""
    # Directamente desde tool_definition_registry por ahora.
    return core_get_all_dynamic_tools()

def get_tool_state_view(tool_name: str) -> dict:
    """Devuelve el estado (activo, postprocess) de una tool."""
    return {
        "active": is_tool_active(tool_name),
        "postprocess": get_tool_postprocess(tool_name)
    }

def get_loading_errors_view() -> list:
    """Devuelve la lista de errores de carga de herramientas."""
    return get_loading_errors()

def get_tool_code_view(tool_name: str) -> str | None:
    """Devuelve el código fuente de una tool."""
    # Llama a la función del core a través del registry
    return get_tool_code(tool_name) 