import os
import streamlit as st
import time
import json
from app.core.tool_manager import (
    load_all_tools, get_all_loaded_tools, get_all_dynamic_tools, 
    set_tool_status, is_tool_active, get_loading_errors
)
from app.core.dynamic_tool_registry import register_tool, persist_tool_to_disk, TOOLS_FOLDER

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
    
    # Cargar contenido del archivo para edición
    tool_path = os.path.join(TOOLS_FOLDER, f"{tool_name}.py")
    try:
        with open(tool_path, "r") as file:
            tool_code = file.read()
        # Guardar en el estado para la edición
        st.session_state.edit_tool = tool_name
        st.session_state.edit_tool_code = tool_code
        st.session_state.edit_tool_is_dynamic = is_dynamic
    except Exception as e:
        st.error(f"No se pudo cargar el archivo: {str(e)}")

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
    Guarda los cambios de edición de una herramienta
    
    Args:
        tool_name: Nombre de la herramienta
        edited_code: Código editado
        is_dynamic: Si es una herramienta dinámica
        
    Returns:
        bool: True si la operación fue exitosa
    """
    tool_path = os.path.join(TOOLS_FOLDER, f"{tool_name}.py")
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
        # Actualizar el resumen de herramientas
        update_tool_summary()
        
        return True
    except Exception as e:
        st.error(f"Error al guardar cambios: {str(e)}")
        return False

def confirm_tool_delete(tool_name):
    """
    Confirma y ejecuta la eliminación de una herramienta
    
    Args:
        tool_name: Nombre de la herramienta a eliminar
        
    Returns:
        bool: True si la operación fue exitosa
    """
    tool_path = os.path.join(TOOLS_FOLDER, f"{tool_name}.py")
    try:
        # Eliminar archivo
        os.remove(tool_path)
        # Marcar como inactiva
        set_tool_status(tool_name, False)
        # Recargar herramientas
        load_all_tools()
        # Actualizar el resumen de herramientas
        update_tool_summary()
        
        return True
    except Exception as e:
        st.error(f"Error al eliminar herramienta: {str(e)}")
        return False

def create_tool(name, schema, code):
    """
    Crea una nueva herramienta
    
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
        
        # Registrar herramienta en memoria - devuelve el nombre correcto
        registered_name = register_tool(tool_name, schema, code)
        
        # Guardar archivo en disco
        success = persist_tool_to_disk(registered_name, schema, code)
        
        # Verificar que el archivo se haya creado
        tool_path = os.path.join(TOOLS_FOLDER, f"{registered_name}.py")
        file_exists = os.path.exists(tool_path)
        
        if not file_exists:
            st.error(f"⚠️ Error: El archivo no se guardó correctamente en {tool_path}")
            
            # Intentar crear el directorio y guardar el archivo directamente
            try:
                os.makedirs(os.path.dirname(tool_path), exist_ok=True)
                with open(tool_path, "w", encoding="utf-8") as f:
                    f.write(code)
                st.success(f"✅ Archivo creado manualmente en {tool_path}")
                file_exists = True
            except Exception as direct_e:
                st.error(f"Error al crear manualmente: {str(direct_e)}")
        
        # Activar la herramienta
        set_tool_status(registered_name, True)
        
        # Recargar herramientas
        load_all_tools()
        
        # Actualizar el resumen de herramientas
        update_tool_summary()
        
        return success and file_exists
    except Exception as e:
        st.error(f"Error al crear la herramienta: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False

def handle_tool_postprocess_toggle(tool_name, postprocess_active):
    """
    Maneja la acción de activar/desactivar el postprocess de una herramienta
    
    Args:
        tool_name: Nombre de la herramienta a modificar
        postprocess_active: True para activar postprocess, False para desactivarlo
    """
    # Determinar si es dinámica o estática
    is_dynamic = tool_name in get_all_dynamic_tools()
    
    # Cargar contenido del archivo para edición
    tool_path = os.path.join(TOOLS_FOLDER, f"{tool_name}.py")
    try:
        with open(tool_path, "r") as file:
            tool_code = file.read()
            
        # Extraer información del código
        namespace = {}
        exec(tool_code, namespace)
        
        if "schema" in namespace:
            # Modificar el valor de postprocess en el schema
            schema = namespace["schema"]
            old_value = schema.get("postprocess", True)
            schema["postprocess"] = postprocess_active
            
            # Crear nuevo código con el schema actualizado
            # Buscar dónde comienza la definición del schema
            schema_lines = tool_code.split('\n')
            schema_start_index = -1
            for i, line in enumerate(schema_lines):
                if line.strip().startswith("schema = {"):
                    schema_start_index = i
                    break
            
            if schema_start_index >= 0:
                # Reemplazar el schema en el código
                schema_json = json.dumps(schema, indent=4, ensure_ascii=False)
                schema_json_lines = [f'schema = {schema_json}']
                
                # Buscar donde termina el schema
                schema_end_index = -1
                bracket_count = 0
                for i in range(schema_start_index, len(schema_lines)):
                    line = schema_lines[i]
                    if '{' in line:
                        bracket_count += line.count('{')
                    if '}' in line:
                        bracket_count -= line.count('}')
                    if bracket_count == 0 and '}' in line:
                        schema_end_index = i
                        break
                
                if schema_end_index >= 0:
                    # Reemplazar las líneas del schema
                    new_code_lines = schema_lines[:schema_start_index] + schema_json_lines + schema_lines[schema_end_index + 1:]
                    new_code = '\n'.join(new_code_lines)
                    
                    # Guardar el archivo modificado
                    with open(tool_path, "w") as file:
                        file.write(new_code)
                    
                    # Si es herramienta dinámica, actualizar en memoria
                    if is_dynamic:
                        register_tool(tool_name, schema, new_code)
                    
                    # Recargar herramientas
                    load_all_tools()
                    update_tool_summary()
                    
                    # Mostrar mensaje
                    if postprocess_active:
                        st.success(f"✅ Postprocess activado para {tool_name}")
                    else:
                        st.warning(f"⚠️ Postprocess desactivado para {tool_name}")
                    
                    # Pequeña pausa para mostrar el mensaje
                    time.sleep(0.3)
                    
                    # Recargar para aplicar cambios
                    st.rerun()
                else:
                    st.error(f"No se pudo encontrar el final del schema en {tool_name}")
            else:
                st.error(f"No se pudo encontrar la definición de schema en {tool_name}")
        else:
            st.error(f"La herramienta {tool_name} no tiene un schema definido")
    except Exception as e:
        st.error(f"Error al modificar postprocess para {tool_name}: {str(e)}")
        import traceback
        st.error(traceback.format_exc()) 