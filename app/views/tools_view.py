import streamlit as st
import os
import json
import time
from app.components.tool_card import render_tool_card
from app.controllers.tool_controller import (
    reload_tools, handle_tool_view, handle_tool_edit, 
    handle_tool_delete, handle_tool_toggle, save_tool_edit,
    confirm_tool_delete, create_tool, handle_tool_postprocess_toggle
)
from app.core.tool_manager import get_all_loaded_tools, get_all_dynamic_tools, is_tool_active, get_loading_errors
from app.utils.ai_generation import generate_tool_with_ai
from app.utils.env_detection import detect_env_variables
from app.core.env_manager import get_env_variables, set_env_variable, reload_env_variables
from app.core.dynamic_tool_registry import TOOLS_FOLDER

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
                reload_tools()
                st.success("✅ Herramientas recargadas exitosamente")
                time.sleep(0.5)  # Pequeña pausa para mostrar el mensaje de éxito
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

    # Generación con IA
    with st.expander("🤖 Generar con IA", expanded=False):
        render_ai_generator()

    # Creación Manual
    with st.expander("✏️ Crear Manualmente", expanded=False):
        render_manual_creation()

def render_static_tools():
    """Renderiza la sección de herramientas estáticas"""
    static_tools = get_all_loaded_tools()
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
                is_active=is_tool_active(k),
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
    dynamic_tools = get_all_dynamic_tools()
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
                is_active=is_tool_active(k),
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
    errors = get_loading_errors()
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
        if "codigo_generado" in st.session_state:
            del st.session_state.codigo_generado
        if "tool_name" in st.session_state:
            del st.session_state.tool_name
        if "tool_schema" in st.session_state:
            del st.session_state.tool_schema
        if "detected_env_vars" in st.session_state:
            del st.session_state.detected_env_vars
    
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
        with st.spinner("Generando código con IA..."):
            try:
                # Verificar API key
                api_key = st.session_state.get("api_key", "")
                if not api_key:
                    st.error("No hay API Key configurada")
                    st.stop()
                    
                # Obtener configuración del modelo
                model_config = st.session_state.get("model_config", {
                    "model": "gpt-4",
                    "temperature": 0.7
                })
                
                # Generar código con la IA
                code = generate_tool_with_ai(
                    st.session_state.ai_prompt, 
                    api_key, 
                    model_config["model"], 
                    model_config["temperature"]
                )
                
                # Guardar el código generado en la sesión para usarlo después
                st.session_state.codigo_generado = code
                
                # Detectar posibles variables de entorno
                env_vars = detect_env_variables(code)
                if env_vars:
                    st.session_state.detected_env_vars = env_vars
                
                # Extraer datos para mostrar información
                try:
                    # Se usa una función local para extraer el nombre y schema
                    namespace = {}
                    exec(code, namespace)
                    func_name = None
                    for name in namespace:
                        if callable(namespace[name]) and name != 'exec' and not name.startswith('__'):
                            func_name = name
                            break
                    
                    if func_name and "schema" in namespace:
                        st.session_state.tool_name = func_name
                        st.session_state.tool_schema = namespace["schema"]
                    else:
                        st.warning("No se pudo extraer el nombre o schema de la herramienta")
                        st.session_state.tool_name = "desconocido"
                        st.session_state.tool_schema = {"description": "No disponible"}
                except Exception as e:
                    st.warning(f"El código se generó pero hubo un problema al extraer metadatos: {str(e)}")
                    st.session_state.tool_name = "desconocido"
                    st.session_state.tool_schema = {"description": "No disponible"}
                
                # Variables de entorno detectadas
                if env_vars:
                    render_detected_env_vars(env_vars)
            except Exception as e:
                st.error(f"❌ Error al generar código: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
    col1, col2 = st.columns(2)
    with col1:
        st.button("🔍 Generar Código", disabled=not ai_prompt, key="generar_codigo", on_click=generate_code_callback)
    with col2:
        st.button("🧹 Limpiar Campos", on_click=clear_ai_form, key="limpiar_campos_interno_generador")
    
    # Mostrar el código generado
    if 'codigo_generado' in st.session_state:
        st.code(st.session_state.codigo_generado, language="python")
        
        # Mensaje adicional de ayuda
        st.success("✅ Código generado correctamente. Revísalo y si te parece correcto, úsalo.")
        
        # Botón para reiniciar (opcional)
        if st.button("🔄 Reiniciar", key="reiniciar_despues_crear"):
            clear_ai_form()
    
        # Mostrar el botón "Usar Esta Herramienta" solo si hay código generado
        st.write("---")
        st.write(f"**Herramienta generada:** `{st.session_state.get('tool_name', 'Herramienta')}`")
        st.write(f"**Descripción:** {st.session_state.get('tool_schema', {}).get('description', 'No disponible')}")
        
        # Definir callback para usar la herramienta
        def use_tool_callback():
            with st.spinner("Procesando y creando herramienta..."):
                try:
                    # Extraer todos los datos necesarios
                    namespace = {}
                    exec(st.session_state.codigo_generado, namespace)
                    
                    func_name = None
                    for name in namespace:
                        if callable(namespace[name]) and name != 'exec' and not name.startswith('__'):
                            func_name = name
                            break
                    
                    if not func_name or "schema" not in namespace:
                        st.error("No se pudo extraer el nombre o schema de la herramienta")
                        st.stop()
                    
                    # Guardar variables de entorno detectadas
                    if "detected_env_vars" in st.session_state and st.session_state.detected_env_vars:
                        # Guardar todas las variables detectadas en .env
                        vars_added = []
                        vars_unchanged = []
                        
                        # Obtener variables existentes para comparación
                        existing_env_vars = get_env_variables()
                        
                        # Mostrar progreso
                        with st.spinner("Guardando variables de entorno..."):
                            for var in st.session_state.detected_env_vars:
                                # Comprobar si la variable ya existe y si se ha modificado
                                if var["name"] in existing_env_vars:
                                    # Si el valor no ha cambiado (o está vacío), mantener el valor existente
                                    if not var.get("value") or var.get("value") == existing_env_vars[var["name"]]:
                                        vars_unchanged.append(var["name"])
                                        continue
                                
                                # Guardar la variable (con o sin valor)
                                result = set_env_variable(var["name"], var.get("value", ""))
                                if result:
                                    vars_added.append(var["name"])
                            
                            # Recargar variables para que estén disponibles inmediatamente
                            if vars_added:
                                reload_env_variables()
                        
                        # Mostrar resultados
                        if vars_added:
                            st.success(f"✅ Variables guardadas/actualizadas en .env: {', '.join(vars_added)}")
                            # Si hay variables sin valor, mostrar un mensaje adicional
                            empty_vars = [var["name"] for var in st.session_state.detected_env_vars if not var.get("value")]
                            if empty_vars:
                                st.info(f"ℹ️ Las siguientes variables se guardaron sin valor y deberás configurarlas en la pestaña 'Variables de Entorno': {', '.join(empty_vars)}")
                        
                        if vars_unchanged:
                            st.info(f"ℹ️ Variables existentes que se mantuvieron sin cambios: {', '.join(vars_unchanged)}")
                        
                        if not vars_added and not vars_unchanged:
                            st.error("⚠️ No se pudieron guardar las variables de entorno")
                    
                    # Crear herramienta
                    success = create_tool(func_name, namespace["schema"], st.session_state.codigo_generado)
                    
                    if success:
                        # Mensaje de éxito
                        st.success(f"✅ Herramienta '{func_name}' creada y activada exitosamente")
                        
                        # Limpiar estado
                        clear_ai_form()
                        
                    else:
                        st.error("❌ No se pudo crear la herramienta")
                            
                except Exception as e:
                    st.error(f"❌ Error al crear la herramienta: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # Botón para usar la herramienta
        st.button("✨ Usar Esta Herramienta", key="usar_herramienta", on_click=use_tool_callback)

def render_detected_env_vars(env_vars):
    """Renderiza la sección de variables de entorno detectadas"""
    if not env_vars:
        return
    
    st.warning(f"⚠️ Se han detectado {len(env_vars)} variables de entorno necesarias para esta herramienta")
    
    # Mostrar formulario para configurar variables
    st.write("### 🔐 Configurar Variables de Entorno")
    st.write("Estas variables son necesarias para que la herramienta funcione correctamente:")
    
    # Comprobar variables existentes en .env
    existing_env_vars = get_env_variables()
    
    # Tabla resumen de variables detectadas
    env_data = [{
        "Variable": var["name"], 
        "Tipo": var["type"], 
        "Descripción": var["description"],
        "Estado": "✅ Ya existe" if var["name"] in existing_env_vars else "🆕 Nueva"
    } for var in env_vars]
    st.dataframe(env_data)
    
    # Formularios para configurar cada variable - SIN USAR EXPANDERS
    st.write("#### Configura los valores de las variables detectadas:")
    
    for i, var in enumerate(env_vars):
        # Usar columnas en lugar de expanders
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**🔑 {var['name']} ({var['type']})**")
            st.write(f"_Descripción:_ {var['description']}")
            st.write(f"_Utilización:_ La herramienta obtiene esta variable mediante `os.getenv(\"{var['name']}\")`")
        
        with col2:
            if var["name"] in existing_env_vars:
                st.info(f"✅ Variable ya configurada")
        
        # Si la variable ya existe, cargar su valor actual
        existing_value = ""
        if var["name"] in existing_env_vars:
            existing_value = existing_env_vars[var["name"]]
            # Pre-asignar el valor existente
            var["value"] = existing_value
            st.session_state.detected_env_vars = env_vars
        
        # Campo para valor, ya sea nuevo o existente
        new_value = st.text_input(
            f"Valor para {var['name']}",
            value=existing_value,  # Mostrar valor existente si lo hay
            type="password",
            key=f"env_var_{i}",
            help=f"{'Valor actual (oculto)' if existing_value else 'Deja vacío para configurarlo más tarde en la sección Variables de Entorno'}"
        )
        
        # Guardar valor en la estructura si cambia
        if new_value:
            var["value"] = new_value
            st.session_state.detected_env_vars = env_vars
        
        # Separador entre variables
        if i < len(env_vars) - 1:
            st.divider()
    
    # Mensaje adicional de ayuda
    st.info("📝 Estas variables se guardarán en el archivo .env cuando uses la herramienta. Variables existentes se mantendrán a menos que ingreses un nuevo valor.")

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
    
    json_schema = st.text_area(
        "Esquema JSON (parámetros)",
        height=150,
        key="generated_schema",
        help="Define los parámetros que acepta la herramienta"
    )
    
    code = st.text_area(
        "Código Python",
        height=200,
        key="generated_code",
        help="Implementación de la herramienta"
    )
    
    # Definir callback para crear herramienta
    def create_tool_callback():
        try:
            with st.spinner("Registrando herramienta..."):
                params = json.loads(st.session_state.generated_schema)
                schema = {
                    "name": st.session_state.generated_name,
                    "description": st.session_state.generated_desc,
                    "parameters": params,
                    "postprocess": st.session_state.generated_postprocess
                }
                success = create_tool(st.session_state.generated_name, schema, st.session_state.generated_code)
            
            if success:
                st.success(f"✅ Herramienta '{st.session_state.generated_name}' creada exitosamente")
                
                # Limpiar el formulario
                clear_manual_form()
                
            else:
                st.error("❌ No se pudo crear la herramienta")
            
        except Exception as e:
            st.error(f"❌ Error al crear la herramienta: {str(e)}")
    
    # Botones con callbacks
    col1, col2 = st.columns(2)
    with col1:
        st.button("✨ Crear Herramienta", on_click=create_tool_callback, disabled=not name)
    with col2:
        st.button("🧹 Limpiar Campos", on_click=clear_manual_form, key="limpiar_campos_interno")

def render_tool_modals():
    """Renderiza los modales para ver, editar y eliminar herramientas"""
    # Modal para visualizar código
    if "view_tool" in st.session_state and "view_tool_code" in st.session_state and st.session_state.view_tool_code:
        tool_name = st.session_state.view_tool
        is_dynamic = st.session_state.get("view_tool_is_dynamic", False)
        
        # Obtener la ruta correcta desde controlador y registro dinámico
        tool_path = os.path.join(TOOLS_FOLDER, f"{tool_name}.py")
        
        st.info(f"📄 Visualizando código de `{tool_name}` ({'herramienta dinámica' if is_dynamic else 'herramienta estática'})")
        try:
            if os.path.exists(tool_path):
                with open(tool_path, "r") as file:
                    tool_code = file.read()
                st.code(tool_code, language="python")
                
                # Botones de acción
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Editar esta herramienta", key=f"edit_from_view_{tool_name}"):
                        handle_tool_edit(tool_name)
                        st.session_state.view_tool_code = False
                        st.rerun()
                with col2:
                    if st.button("🗑️ Eliminar esta herramienta", key=f"delete_from_view_{tool_name}"):
                        handle_tool_delete(tool_name)
                        st.session_state.view_tool_code = False
                        st.rerun()
                
                # Botón para cerrar
                if st.button("❌ Cerrar", key="close_view"):
                    st.session_state.view_tool_code = False
                    if "view_tool_is_dynamic" in st.session_state:
                        del st.session_state.view_tool_is_dynamic
                    st.rerun()
            else:
                st.error(f"⚠️ El archivo no existe en la ruta: {tool_path}")
                st.warning(f"Es posible que la herramienta esté registrada en memoria pero el archivo no se haya guardado correctamente.")
                st.warning(f"Ruta actual del script: {os.path.dirname(os.path.abspath(__file__))}")
                st.warning(f"Directorio app: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
                st.warning(f"Herramientas cargadas: {list(get_all_loaded_tools().keys())}")
                st.warning(f"Herramientas dinámicas: {list(get_all_dynamic_tools().keys())}")
                
                # Botón para cerrar
                if st.button("❌ Cerrar", key="close_view_missing"):
                    st.session_state.view_tool_code = False
                    if "view_tool_is_dynamic" in st.session_state:
                        del st.session_state.view_tool_is_dynamic
                    st.rerun()
        except Exception as e:
            st.error(f"Error al leer el código: {str(e)}")
            st.warning(f"Ruta del archivo: {tool_path}")
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