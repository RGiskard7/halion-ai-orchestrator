import streamlit as st
from app.components.tool_card import render_tool_card
from app.controllers.tool_controller import (
    reload_tools, update_tool_summary, # Generales
    handle_tool_view, handle_tool_edit, handle_tool_delete, handle_tool_toggle, # Acciones tarjeta
    handle_tool_postprocess_toggle, # Acción tarjeta
    handle_generate_tool_ai, handle_create_generated_tool, # Generación AI
    handle_create_manual_tool, # Creación manual
    # Nuevas funciones para obtener datos para la vista:
    get_static_tools_view, get_dynamic_tools_view, get_tool_state_view,
    get_loading_errors_view, get_tool_code_view,
    save_tool_edit, confirm_tool_delete
)
from app.core.env_manager import get_env_variables
import json

def render():
    """
    Renderiza la vista de gestión de herramientas
    """
    col1, col2 = st.columns([3,1])
    with col1:
        st.subheader("🔄 Gestión de Herramientas")
    with col2:
        if st.button("🔄 Recargar Herramientas", help="Recarga todas las herramientas desde el disco"):
            with st.spinner("Recargando herramientas..."):
                if reload_tools():
                    st.success("✅ Herramientas recargadas exitosamente")
            st.rerun()
    
    # Herramientas Estáticas
    with st.expander("📁 Herramientas Estáticas", expanded=True):
        render_static_tools()
    
    # Herramientas Dinámicas
    with st.expander("💫 Herramientas Dinámicas", expanded=True):
        render_dynamic_tools()

    # Errores de Carga
    with st.expander("🚨 Errores de Carga", expanded=False):
        render_loading_errors()
    
    # Modales para herramientas (ahora justo después de los errores de carga)
    render_tool_modals()

    st.divider()
    
    # Nueva Herramienta
    st.subheader("➕ Crear Nueva Herramienta")

    # Inicializar el estado de los expanders si no existe
    if "expander_ai_generator_open" not in st.session_state:
        st.session_state.expander_ai_generator_open = False
    if "expander_manual_creation_open" not in st.session_state:
        st.session_state.expander_manual_creation_open = False

    # Generación con IA
    with st.expander("🤖 Generar con IA", expanded=st.session_state.expander_ai_generator_open):
        render_ai_generator()

    # Creación Manual
    with st.expander("✏️ Crear Manualmente", expanded=st.session_state.expander_manual_creation_open):
        render_manual_creation()

def render_static_tools():
    """Renderiza la sección de herramientas estáticas"""
    static_tools = get_static_tools_view()
    if static_tools:
        # Paginación para herramientas estáticas
        items_per_page = 5  # Cantidad de herramientas por página
        total_tools = len(static_tools)
        total_pages = (total_tools + items_per_page - 1) // items_per_page  # Redondear hacia arriba
        
        # Inicializar el estado de la página si no existe
        if "static_tools_page" not in st.session_state:
            st.session_state.static_tools_page = 1
        
        # Controles de paginación
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("⬅️ Anterior", key="prev_static", disabled=st.session_state.static_tools_page <= 1):
                st.session_state.static_tools_page -= 1
                st.rerun()
        with col2:
            st.write(f"Página {st.session_state.static_tools_page} de {max(1, total_pages)} ({total_tools} herramientas)")
        with col3:
            if st.button("Siguiente ➡️", key="next_static", disabled=st.session_state.static_tools_page >= total_pages):
                st.session_state.static_tools_page += 1
                st.rerun()
        
        # Calcular qué herramientas mostrar en esta página
        start_idx = (st.session_state.static_tools_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_tools)
        
        # Obtener las keys ordenadas para poder paginarlas
        tool_keys = sorted(list(static_tools.keys()))[start_idx:end_idx]
        
        # Mostrar las herramientas de esta página
        for k in tool_keys:
            v = static_tools[k]
            render_tool_card(
                tool_name=k,
                tool_info=v,
                is_active=get_tool_state_view(k)["active"],
                on_view=handle_tool_view,
                on_edit=handle_tool_edit,
                on_delete=handle_tool_delete,
                on_toggle=handle_tool_toggle,
                on_postprocess_toggle=handle_tool_postprocess_toggle,
                card_type="static"
            )
    else:
        st.info("ℹ️ No hay herramientas estáticas cargadas")

def render_dynamic_tools():
    """Renderiza la sección de herramientas dinámicas"""
    dynamic_tools = get_dynamic_tools_view()
    if dynamic_tools:
        # Paginación para herramientas dinámicas
        items_per_page = 5  # Cantidad de herramientas por página
        total_tools = len(dynamic_tools)
        total_pages = (total_tools + items_per_page - 1) // items_per_page  # Redondear hacia arriba
        
        # Inicializar el estado de la página si no existe
        if "dynamic_tools_page" not in st.session_state:
            st.session_state.dynamic_tools_page = 1
        
        # Controles de paginación
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("⬅️ Anterior", key="prev_dynamic", disabled=st.session_state.dynamic_tools_page <= 1):
                st.session_state.dynamic_tools_page -= 1
                st.rerun()
        with col2:
            st.write(f"Página {st.session_state.dynamic_tools_page} de {max(1, total_pages)} ({total_tools} herramientas)")
        with col3:
            if st.button("Siguiente ➡️", key="next_dynamic", disabled=st.session_state.dynamic_tools_page >= total_pages):
                st.session_state.dynamic_tools_page += 1
                st.rerun()
        
        # Calcular qué herramientas mostrar en esta página
        start_idx = (st.session_state.dynamic_tools_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_tools)
        
        # Obtener las keys ordenadas para poder paginarlas
        tool_keys = sorted(list(dynamic_tools.keys()))[start_idx:end_idx]
        
        # Mostrar las herramientas de esta página
        for k in tool_keys:
            v = dynamic_tools[k]
            render_tool_card(
                tool_name=k,
                tool_info=v,
                is_active=get_tool_state_view(k)["active"],
                on_view=handle_tool_view,
                on_edit=handle_tool_edit,
                on_delete=handle_tool_delete,
                on_toggle=handle_tool_toggle,
                on_postprocess_toggle=handle_tool_postprocess_toggle,
                card_type="dynamic"
            )
    else:
        st.info("ℹ️ No hay herramientas dinámicas registradas")

def render_loading_errors():
    """Renderiza la sección de errores de carga"""
    errors = get_loading_errors_view()
    if errors:
        for e in errors:
            st.error(f"📄 {e['file']}\n```\n{e['error']}\n```")
    else:
        st.success("✅ No se encontraron errores de carga")

def render_ai_generator():
    """Renderiza la sección de generación de herramientas con IA"""
    # Definir callback para limpiar
    def clear_ai_form():
        st.session_state.ai_prompt = ""
        # Limpiar el estado de generación en la sesión
        st.session_state.generated_code = None
        st.session_state.generated_tool_name = None
        st.session_state.generated_schema = None
        st.session_state.generated_env_vars = None
        st.session_state.generation_error = None
        st.session_state.expander_ai_generator_open = False
    
    st.markdown("#### Generador de Herramientas con IA")
    
    # Inicializar ai_prompt si no existe
    if "ai_prompt" not in st.session_state:
        st.session_state.ai_prompt = ""
    
    ai_prompt = st.text_area(
        "Describe la herramienta que necesitas",
        key="ai_prompt",
        help="Describe en lenguaje natural qué quieres que haga la herramienta. Por ejemplo: 'Necesito una herramienta que traduzca texto a código morse y viceversa'",
        placeholder="Ejemplo: Una herramienta que calcule el IMC dado el peso en kg y la altura en metros..."
    )
    
    # Definir callback para generar código
    def generate_code_callback():
        # Llamar al controlador para manejar la generación y actualización del estado
        with st.spinner("Generando y analizando código..."):
            handle_generate_tool_ai(st.session_state.ai_prompt)
        st.session_state.expander_ai_generator_open = True

    # Mostrar error de generación si existe (poblado por el controlador)
    if st.session_state.get("generation_error"):
        st.error(f"❌ Error en Generación: {st.session_state.generation_error}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("🔍 Generar Código", disabled=not ai_prompt, key="generar_codigo", on_click=generate_code_callback)
    with col2:
        st.button("🧹 Limpiar Campos", on_click=clear_ai_form, key="limpiar_campos_interno_generador")
    
    # Mostrar el código generado
    generated_code = st.session_state.get("generated_code")
    if generated_code:
        st.code(generated_code, language="python")

        # Mostrar metadatos extraídos (si existen)
        tool_name = st.session_state.get("generated_tool_name")
        schema = st.session_state.get("generated_schema")
        env_vars = st.session_state.get("generated_env_vars")

        if tool_name and schema:
            # Asegurar que schema es un dict antes de acceder a .get
            schema_dict = schema
            if isinstance(schema, str):
                try:
                    schema_dict = json.loads(schema)
                except Exception:
                    schema_dict = {}
            st.success(f"✅ Código generado para la herramienta '{tool_name}'.")
            st.write(f"**Descripción:** {schema_dict.get('description', 'No disponible')}")
        else:
            st.warning("⚠️ Código generado, pero no se pudo extraer nombre/schema. Revísalo manualmente.")

        # Renderizar sección para configurar env vars detectadas
        render_detected_env_vars(env_vars if env_vars else [])
        
        # Botón para Usar/Crear la herramienta
        st.write("--- --- ---")
        if st.button("✨ Crear Herramienta Generada", key="usar_herramienta_generada"):
            # Verificar que tenemos lo mínimo necesario (código)
            if generated_code:
                # El schema puede ser None si falló la extracción, el controlador lo manejará
                # Pasar las env_vars tal como están en el estado (pueden haber sido modificadas por el usuario)
                current_env_vars = st.session_state.get("generated_env_vars", [])
                handle_create_generated_tool(
                    tool_name if tool_name else "generated_tool", # Usar un nombre por defecto si no se extrajo
                    schema if schema else {}, # Pasar schema vacío si no se extrajo
                    generated_code,
                    current_env_vars
                )
            else:
                st.error("No hay código generado para crear la herramienta.")
        # Botón para reiniciar (limpiar todo)
        if st.button("🔄 Descartar Generación", key="descartar_generacion"):
            clear_ai_form()

def render_detected_env_vars(env_vars):
    """Renderiza la sección de variables de entorno detectadas"""
    if not env_vars:
        return
    
    st.warning(f"⚠️ Se han detectado {len(env_vars)} variables de entorno necesarias para esta herramienta")
    
    # Mostrar formulario para configurar variables
    st.write("### 🔐 Configurar Variables de Entorno")
    st.write("Estas variables son necesarias para que la herramienta funcione correctamente:")
    
    # Tabla resumen de variables detectadas
    env_data = [{
        "Variable": var["name"], 
        "Tipo": var["type"], 
        "Descripción": var["description"],
        "Estado": "✅ Ya existe" if var["name"] in get_env_variables() else "🆕 Nueva"
    } for var in env_vars]
    st.dataframe(env_data)
    
    # Inputs para configurar valores (si el usuario quiere)
    if env_vars: # Solo mostrar si hay variables
        st.write("#### Configura los valores de las variables detectadas (opcional):")
    
    for i, var in enumerate(env_vars):
        # Usamos una clave única para el input
        input_key = f"env_var_input_{var['name']}"
        new_value = st.text_input(
            f"Valor para {var['name']}",
            value=var.get("value", ""), # Mostrar valor si ya existe en el estado
            type="password",
            key=input_key,
            help="Deja vacío para usar el valor existente en .env (si existe) o para configurarlo más tarde."
        )
        
        # Guardar valor en la estructura si cambia
        if new_value != var.get("value", ""):
            # Buscar el índice correcto en la lista del estado
            for idx, state_var in enumerate(st.session_state.generated_env_vars):
                if state_var['name'] == var['name']:
                    st.session_state.generated_env_vars[idx]['value'] = new_value
                    break
            var['value'] = new_value
        
        # Separador entre variables
        if i < len(env_vars) - 1:
            st.divider()
    
    # Mensaje adicional de ayuda
    st.info("📝 Al crear la herramienta, se intentará guardar estos valores en el archivo .env. Si dejas un valor vacío, se usará el valor actual de .env si existe. Si no existe, deberás configurarlo manualmente.")

def render_manual_creation():
    """Renderiza la sección de creación manual de herramientas"""
    # Definir callback para limpiar el formulario
    def clear_manual_form():
        st.session_state.generated_name = ""
        st.session_state.generated_desc = ""
        st.session_state.generated_schema = """{
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Primer parámetro"
                }
            },
            "required": ["param1"]
        }"""
        st.session_state.generated_code = """def nueva_herramienta(param1):
            '''
            Documentación de la herramienta
            '''
            return f"Procesando: {param1}"
        """
        st.session_state.generated_postprocess = True
        st.session_state.expander_manual_creation_open = False
    
    st.markdown("#### Crear Nueva Herramienta Manualmente")
            
    # Inicializar valores por defecto si no existen
    if "generated_name" not in st.session_state:
        st.session_state.generated_name = ""
    if "generated_desc" not in st.session_state:
        st.session_state.generated_desc = ""
    if "generated_schema" not in st.session_state:
        st.session_state.generated_schema = """{
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Primer parámetro"
                }
            },
            "required": ["param1"]
        }"""
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = """def nueva_herramienta(param1):
            '''
            Documentación de la herramienta
            '''
            return f"Procesando: {param1}"
        """
    if "generated_postprocess" not in st.session_state:
        st.session_state.generated_postprocess = True
            
    # Crear inputs fuera del formulario para poder manipularlos con callbacks
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        name = st.text_input(
            "Nombre",
            key="generated_name",
            help="Nombre único para la herramienta"
        )
    with col2:
        desc = st.text_input(
            "Descripción",
            key="generated_desc",
            help="Breve descripción de su función"
        )
    with col3:
        postprocess = st.toggle(
            "Post-procesado",
            key="generated_postprocess",
            help="Si está activado, la IA procesará el resultado. Si está desactivado, se mostrará el resultado directo de la herramienta."
        )
    
    # --- Forzar que session_state.generated_schema sea siempre string ---
    if isinstance(st.session_state.generated_schema, dict):
        st.session_state.generated_schema = json.dumps(st.session_state.generated_schema, indent=2, ensure_ascii=False)
    elif st.session_state.generated_schema is None:
        st.session_state.generated_schema = ""
    # --- FIN forzado ---
    
    json_schema = st.text_area(
        "Esquema JSON (parámetros)",
        height=150,
        key="generated_schema",
        help="Define los parámetros que acepta la herramienta"
    )

    # --- Validación visual de JSON en tiempo real ---
    is_json_valid = True
    json_error_msg = ""
    try:
        json.loads(st.session_state.generated_schema)
    except Exception as e:
        is_json_valid = False
        json_error_msg = str(e)
    if not is_json_valid:
        st.error(f"❌ El esquema JSON no es válido: {json_error_msg}")
    # --- FIN validación visual ---
    
    code = st.text_area(
        "Código Python",
        height=200,
        key="generated_code",
        help="Implementación de la herramienta"
    )
    
    # Definir callback para crear herramienta
    def create_tool_callback():
        # Validar y parsear JSON del schema aquí en la vista
        try:
            params = json.loads(st.session_state.generated_schema)
            schema = {
                "name": st.session_state.generated_name.strip(),
                "description": st.session_state.generated_desc.strip(),
                "parameters": params,
                "postprocess": st.session_state.generated_postprocess # Este se obtiene del manager ahora
            }
            code = st.session_state.generated_code

            # Llamar al controlador para manejar la creación
            if handle_create_manual_tool(schema["name"], schema, code): # Usar nombre del schema
                st.success(f"✅ Herramienta '{schema['name']}' creada exitosamente")
                # Limpiar el formulario
                clear_manual_form()
                st.session_state.expander_manual_creation_open = True
            else:
                st.error("❌ No se pudo crear la herramienta")
            
        except json.JSONDecodeError as json_e:
            st.error(f"❌ Error en el formato JSON del schema: {json_e}")
        except Exception as e: # Otros errores
            st.error(f"❌ Error al crear la herramienta: {str(e)}")
    
    # Botones con callbacks
    col1, col2 = st.columns(2)
    with col1:
        st.button("✨ Crear Herramienta", on_click=create_tool_callback, disabled=not name or not is_json_valid)
    with col2:
        st.button("🧹 Limpiar Campos", on_click=clear_manual_form, key="limpiar_campos_interno")

def render_tool_modals():
    """Renderiza los modales para ver, editar y eliminar herramientas"""
    # Modal para visualizar código
    if "view_tool" in st.session_state and "view_tool_code" in st.session_state and st.session_state.view_tool_code:
        tool_name = st.session_state.view_tool
        is_dynamic = st.session_state.get("view_tool_is_dynamic", False)
        
        # Obtener código exclusivamente desde el controlador
        tool_code = get_tool_code_view(tool_name)
        # TODO: Crear get_tool_code_view() en el controlador

        st.info(f"📄 Visualizando código de `{tool_name}` ({'dinámica' if is_dynamic else 'estática'})")
        try:
            if tool_code is not None:
                st.code(tool_code, language="python")
                
                # Botones de acción
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Editar esta herramienta", key=f"edit_from_view_{tool_name}"):
                        handle_tool_edit(tool_name)
                        st.session_state.view_tool_code = False
                        # No rerun aquí, handle_tool_edit prepara el estado para el modal
                        st.rerun()
                with col2:
                    if st.button("🗑️ Eliminar esta herramienta", key=f"delete_from_view_{tool_name}"):
                        handle_tool_delete(tool_name)
                        st.session_state.view_tool_code = False
                        # No rerun aquí, handle_tool_delete prepara el estado para el modal
                        st.rerun()
                
                # Botón para cerrar
                if st.button("❌ Cerrar", key="close_view"):
                    st.session_state.view_tool_code = False
                    if "view_tool_is_dynamic" in st.session_state:
                        del st.session_state.view_tool_is_dynamic
                    st.rerun()
            else:
                st.error("⚠️ No se pudo obtener el código para la herramienta '{tool_name}'.")
                
                # Botón para cerrar
                if st.button("❌ Cerrar", key="close_view_missing"):
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
            success = handle_tool_edit(tool_name, edited_code, is_dynamic)
            success = save_tool_edit(tool_name, edited_code, is_dynamic)
            if success:
                st.success(f"✅ Herramienta '{tool_name}' actualizada correctamente")
                # Limpiar estado
                del st.session_state.edit_tool
                del st.session_state.edit_tool_code
                if "edit_tool_is_dynamic" in st.session_state:
                    del st.session_state.edit_tool_is_dynamic
                st.rerun()
        
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
                success = handle_tool_delete(tool_name)
                success = confirm_tool_delete(tool_name)
                if success:
                    st.success(f"✅ Herramienta '{tool_name}' eliminada correctamente")
                    # Limpiar estado
                    del st.session_state.delete_tool
                    if "delete_tool_is_dynamic" in st.session_state:
                        del st.session_state.delete_tool_is_dynamic
                    st.rerun()
        with col2:
            if st.button("❌ No, cancelar", key=f"cancel_delete_{tool_name}"):
                # Limpiar estado
                del st.session_state.delete_tool
                if "delete_tool_is_dynamic" in st.session_state:
                    del st.session_state.delete_tool_is_dynamic
                st.rerun() 