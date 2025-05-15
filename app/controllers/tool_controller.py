import os
import streamlit as st
import time
import traceback
import json
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
        schema: Schema JSON de la herramienta (puede ser dict o str JSON)
        code: Código de la herramienta
        
    Returns:
        bool: True si la operación fue exitosa
    """
    schema_dict: dict
    try:
        # Asegurarse de que el schema sea un diccionario
        if isinstance(schema, str):
            try:
                schema_dict = json.loads(schema)
            except json.JSONDecodeError as e:
                st.error(f"Error al decodificar el JSON del schema: {e}. Schema recibido: {schema}")
                return False, name # Devolver el nombre original como intentado
        elif isinstance(schema, dict):
            schema_dict = schema
        else:
            st.error(f"El schema proporcionado no es ni un string JSON válido ni un diccionario. Tipo recibido: {type(schema)}")
            return False, name # Devolver el nombre original como intentado

        # Obtener el nombre correcto del schema_dict
        tool_name = schema_dict.get("name", name)
        
        # Intentar registrar en memoria primero (valida el código)
        registered_name: str | None = None
        try:
            registered_name = register_tool(tool_name, schema_dict, code) # Usar schema_dict
        except Exception as reg_e:
            st.error(f"Error al registrar la herramienta en memoria: {reg_e}")
            return False, tool_name # Nombre que se intentó registrar
        
        if not registered_name: # Por si register_tool devuelve None en algún caso no esperado
            st.error("Error interno: El registro de la herramienta no devolvió un nombre.")
            return False, tool_name

        # Guardar archivo en disco
        success_persist = persist_tool_to_disk(registered_name, schema_dict, code) # Usar schema_dict
        
        if not success_persist:
            st.error(f"Error al guardar el archivo para la herramienta '{registered_name}'. Ver logs para detalles.")
            return False, registered_name
        
        # Activar la herramienta
        set_tool_status(registered_name, True)
        
        # Recargar herramientas
        load_all_tools()
        
        # Actualizar el resumen de herramientas
        update_tool_summary()
        
        return True, registered_name # Éxito
    except Exception as e:
        st.error(f"Error al crear la herramienta: {str(e)}")
        print(f"[Controller Error] Traceback al crear tool: {traceback.format_exc()}")
        return False, name # Nombre original en caso de excepción mayor

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
    # El tipo de retorno ahora es Tuple[bool, Optional[str]]
    # (éxito, nombre_final_de_herramienta)
    final_tool_name_on_failure: str | None = tool_name # Nombre a devolver si falla antes de _create_and_persist_tool
    try:
        # 1. Guardar variables de entorno detectadas (y posiblemente modificadas por el usuario)
        if env_vars_with_values:
            with st.spinner("Guardando variables de entorno detectadas..."):
                saved_vars, unchanged_vars = tool_service.save_detected_env_vars(env_vars_with_values)
            if saved_vars:
                st.success(f"✅ Variables guardadas/actualizadas en .env: {', '.join(saved_vars)}")
            if unchanged_vars:
                st.info(f"ℹ️ Variables existentes sin cambios: {', '.join(unchanged_vars)}")
            # Considerar mostrar error si save_detected_env_vars falla y retornar False, tool_name?

        # 2. Crear y persistir la herramienta
        with st.spinner(f"Creando y guardando herramienta '{tool_name}'..."):
            # _create_and_persist_tool espera el nombre potencial y el schema (que puede ser str o dict)
            # tool_name aquí es el nombre sugerido por la IA o "generated_tool"
            creation_success, final_tool_name = _create_and_persist_tool(tool_name, schema, code)
            final_tool_name_on_failure = final_tool_name # Actualizar el nombre a devolver en caso de fallo posterior

        if creation_success:
            # st.toast(f"✅ Herramienta '{final_tool_name}' creada y activada exitosamente.", icon="🎉") # ELIMINAR TOAST DE AQUÍ
            # Limpiar estado de generación AI en la sesión con prefijos ai_
            # La clave ai_prompt será limpiada por clear_ai_form() en la vista.
            if "ai_tool_code" in st.session_state: del st.session_state.ai_tool_code
            if "ai_tool_name" in st.session_state: del st.session_state.ai_tool_name
            if "ai_tool_schema" in st.session_state: del st.session_state.ai_tool_schema
            if "ai_tool_env_vars" in st.session_state: del st.session_state.ai_tool_env_vars
            if "generation_error" in st.session_state: del st.session_state.generation_error # Error específico de IA
            return True, final_tool_name # Devolver éxito y el nombre final
        else:
            # El error específico ya se mostró en _create_and_persist_tool
            return False, final_tool_name # Devolver fallo y el nombre que se intentó

    except Exception as e:
        st.error(f"Error general al procesar la herramienta generada: {e}")
        print(f"[Controller Error] Traceback al crear tool generada: {traceback.format_exc()}")
        return False, final_tool_name_on_failure # Devolver fallo y el último nombre conocido

def handle_generate_tool_ai(description: str):
    """
    Orquesta la generación de código de tool con IA y la extracción de metadatos/env vars.
    Actualiza st.session_state con los resultados o errores.
    """
    # Limpiar estado previo de las claves de IA y el error específico
    st.session_state.ai_tool_code = None
    st.session_state.ai_tool_name = None
    st.session_state.ai_tool_schema = None
    st.session_state.ai_tool_env_vars = None
    st.session_state.generation_error = None # Error específico de este flujo

    try:
        # Obtener API key y configuración del modelo desde st.session_state
        # Estos deberían ser establecidos por la vista de chat/configuración.
        api_key = st.session_state.get("api_key") 
        model_config = st.session_state.get("model_config", {})

        if not api_key:
            error_msg = "API Key de OpenAI no configurada. Por favor, configúrala en la sección de Chat o Administración."
            st.session_state.generation_error = error_msg
            st.error(error_msg)
            st.session_state.expander_ai_generator_open = True
            return # No se puede continuar sin API Key

        # Paso 1: Generar el código de la herramienta usando el servicio
        generated_code = tool_service.generate_tool_code_via_ai(description, api_key, model_config)
        
        if not generated_code:
            # Si el servicio de generación de código devuelve None o vacío, es un error.
            error_msg = "La generación de código no produjo ningún resultado."
            st.session_state.generation_error = error_msg
            st.error(error_msg)
            st.session_state.expander_ai_generator_open = True
            return

        st.session_state.ai_tool_code = generated_code # Guardar el código generado

        # Paso 2: Extraer metadatos (nombre, schema) y variables de entorno del código generado
        tool_name, schema, env_vars = tool_service.extract_tool_metadata_and_env_vars(generated_code)
        
        # Poblar el estado de la sesión con los resultados extraídos
        st.session_state.ai_tool_name = tool_name
        
        if isinstance(schema, dict):
            try:
                st.session_state.ai_tool_schema = json.dumps(schema, indent=2, ensure_ascii=False)
            except Exception:
                st.session_state.ai_tool_schema = str(schema) # Fallback a string
        elif isinstance(schema, str): # Si ya es un string JSON
             st.session_state.ai_tool_schema = schema
        else:
            st.session_state.ai_tool_schema = "{}" # Default si no es dict ni str
        
        st.session_state.ai_tool_env_vars = env_vars if env_vars is not None else []

        if not tool_name or not schema:
            st.warning("⚠️ No se pudieron extraer completamente el nombre o el schema del código generado. Revisa el código y complétalo manualmente si es necesario.")
            # No es un error fatal, el usuario puede editar.

        st.session_state.expander_ai_generator_open = True # Mantener expander abierto para mostrar resultados

    except ValueError as ve: # Capturar ValueError específico de la falta de API key en el servicio
        st.session_state.generation_error = str(ve)
        st.error(str(ve))
        st.session_state.expander_ai_generator_open = True

    except Exception as e:
        # Manejar otras excepciones inesperadas durante el proceso
        detailed_error = f"Error durante la generación o análisis de la herramienta: {str(e)}"
        st.session_state.generation_error = detailed_error
        st.session_state.expander_ai_generator_open = True # Mantener expander abierto
        st.error(detailed_error) # Mostrar error inmediatamente
        print(f"[Controller Error] Traceback en handle_generate_tool_ai: {traceback.format_exc()}")

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