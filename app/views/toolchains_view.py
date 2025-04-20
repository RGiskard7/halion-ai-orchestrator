# app/views/toolchains_view.py

import streamlit as st
# Importar el controlador
from app.controllers import toolchain_controller as tc_controller
from app.models.toolchain_model import Toolchain, ToolchainStep
# La vista ya no necesita importar tool_manager, os, json, time, ai_generation

def render():
    """
    Renderiza la vista completa de gestión de Toolchains
    """
    st.subheader("🔁 Gestión de Toolchains")

    # Recarga desde archivo -> ahora a través del controlador
    toolchains = tc_controller.get_all_toolchains_view()

    # Listado con ejecución y control
    with st.expander("📜 Toolchains Disponibles", expanded=True):
        render_toolchains_list(toolchains)

    # Errores (en futuro, si añadimos validación)
    # with st.expander("🚨 Errores de Carga", expanded=False):
    #     render_toolchain_errors()

    st.divider()

    # Creación manual o por IA
    render_manual_creator()
    render_toolchain_editor(toolchains) # 🔧 Editor (si hay edición activa)
    render_ai_creator()
    render_toolchain_modals(toolchains)


def render_toolchains_list(toolchains):
    """
    Lista todas las toolchains con opciones de ejecución, edición o eliminación
    """
    if not toolchains:
        st.info("ℹ️ No hay toolchains definidas todavía")
        return

    for tc in toolchains:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {tc.name}")
                st.caption(tc.description)
                st.markdown("**Pasos:**")
                for i, step in enumerate(tc.steps, 1):
                    st.markdown(f"{i}. `{step.tool_name}` ← {step.input_map}")
            with col2: # Usar el controlador para gestionar el estado
                st.button("▶️ Ejecutar", key=f"exec_{tc.name}", on_click=tc_controller.set_toolchain_to_run, args=(tc.name,))
                st.button("✏️ Editar", key=f"edit_{tc.name}", on_click=tc_controller.set_toolchain_to_edit, args=(tc.name,))
                st.button("🗑️ Borrar", key=f"delete_{tc.name}", on_click=tc_controller.set_toolchain_to_delete, args=(tc.name,))

    # Ver si se quiere ejecutar
    if "run_toolchain" in st.session_state:
        # Obtener la toolchain a través del controlador podría ser más seguro si la lista cambió
        selected_name = st.session_state.run_toolchain
        selected = tc_controller.get_toolchain_view(selected_name)

        if selected:
            st.markdown("---")
            st.markdown(f"### 🚀 Ejecutar Toolchain: `{selected.name}`")

            # Determinar las claves iniciales necesarias
            initial_keys = set()
            for step in selected.steps:
                initial_keys.update(step.input_map.values())

            inputs = {}
            for k in sorted(initial_keys):
                # Usar claves únicas en session_state para los inputs
                input_key = f"input_{selected.name}_{k}"
                inputs[k] = st.text_input(f"Input: {k}", key=input_key)

            col1, col2 = st.columns(2)
            with col1:
                launch = st.button("▶️ Lanzar Toolchain", key=f"launch_{selected.name}")
            with col2:
                # Usar el controlador para cancelar/limpiar estado
                cancel = st.button("❌ Cancelar", key=f"cancel_run_{selected.name}", on_click=tc_controller.clear_toolchain_to_run)

            if launch:
                # Llamar al controlador para manejar la ejecución
                with st.spinner(f"Ejecutando toolchain '{selected.name}'..."):
                    tc_controller.handle_run_toolchain(selected.name, inputs)

                # Mostrar resultados/errores desde el estado de sesión poblado por el controlador
                if st.session_state.get("toolchain_run_error"):
                    st.error(f"❌ Error en la ejecución: {st.session_state.toolchain_run_error}")
                if st.session_state.get("toolchain_run_steps_log"):
                    st.markdown("## 🧪 Ejecución paso a paso")
                    for log_entry in st.session_state.toolchain_run_steps_log:
                        st.markdown(f"### 🔹 Paso {log_entry['step']}: `{log_entry['tool_name']}`")
                        st.markdown("**Inputs:**")
                        st.json(log_entry['inputs'])
                        if log_entry['status'] == 'SUCCESS':
                            st.success(f"✅ Ejecutado correctamente en {log_entry['duration_seconds']:.4f} segundos")
                            st.markdown("**Output:**")
                            st.json(log_entry['output'])
                        elif log_entry['status'] == 'ERROR':
                            st.error(f"❌ Error: {log_entry['error']}")
                        st.caption(f"Duración: {log_entry['duration_seconds']:.4f}s")

                if st.session_state.get("toolchain_run_result") is not None:
                     st.markdown("---")
                     st.markdown("## 🧾 Contexto final")
                     st.json(st.session_state.toolchain_run_result)

                # Limpiar el estado de ejecución después de mostrar los resultados
                # Esto podría hacerse automáticamente si el flujo lo requiere,
                # o mantenerlo hasta que el usuario cancele explícitamente.
                # Por ahora, lo limpiamos aquí para permitir nuevas ejecuciones.
                # tc_controller.clear_toolchain_to_run() # Comentado: dejar que Cancelar lo haga explícitamente

        else:
            # Si selected es None, significa que la toolchain marcada para correr ya no existe.
            # Limpiar el estado.
            st.warning(f"La toolchain '{st.session_state.run_toolchain}' ya no existe.")
            tc_controller.clear_toolchain_to_run()

def render_manual_creator():
    """
    Formulario de creación manual de nuevas toolchains, con actualización dinámica de pasos.
    """
    with st.expander("✏️ Crear Toolchain Manualmente", expanded=False):
        # La limpieza ahora la maneja el controlador después de guardar con éxito.
        # Podemos mantener una limpieza simple de UI si el usuario quiere cancelar.
        def clear_ui_manual_form():
            st.session_state.new_tc_name = ""
            st.session_state.new_tc_desc = ""
            st.session_state.new_tc_steps = 1 # Resetear número de pasos
            for i in range(st.session_state.get("manual_steps_count", 1)): # Limpiar solo los campos visibles
                 st.session_state[f"new_tool_{i}"] = ""
                 st.session_state[f"new_map_{i}"] = ""

        st.markdown("### Crear Nueva Toolchain")
            
        # Inicializar número de pasos
        if "new_tc_steps" not in st.session_state:
            st.session_state.new_tc_steps = 1

        # Selector de pasos (FUERA del formulario para reactividad)
        st.markdown("### 🔢 Configuración de pasos")
        st.session_state.new_tc_steps = st.number_input(
            label="Cantidad de pasos",
            min_value=1,
            max_value=10,
            value=st.session_state.new_tc_steps,
            step=1,
            key="manual_steps_count"
        )

        # Inicializar valores por defecto
        if "new_tc_name" not in st.session_state:
            st.session_state.new_tc_name = ""
        if "new_tc_desc" not in st.session_state:
            st.session_state.new_tc_desc = ""
                
        # Campos del formulario directamente (sin st.form)
        name = st.text_input("Nombre único de la Toolchain", key="new_tc_name")
        desc = st.text_area("Descripción", key="new_tc_desc")

        raw_steps = []
        for i in range(st.session_state.new_tc_steps):
            st.markdown(f"**Paso {i + 1}**")
            tool_name = st.text_input(f"Tool del Paso {i + 1}", key=f"new_tool_{i}")
            map_text = st.text_area(
                f"Input map (clave:valor por línea)",
                key=f"new_map_{i}",
                placeholder="Ejemplo:\ntexto: resumen\nidioma: idioma_destino"
            )
            raw_steps.append((tool_name, map_text))

        # Botones con callbacks
        col1, col2 = st.columns(2)
        with col1:
            # Llamar al controlador para guardar
            st.button("💾 Guardar Toolchain", key="guardar_toolchain",
                      on_click=tc_controller.handle_save_new_toolchain,
                      args=(name, desc, raw_steps),
                      disabled=not name)
        with col2:
            st.button("🧹 Limpiar Campos", key="limpiar_campos_toolchain", on_click=clear_ui_manual_form)

def render_toolchain_editor(toolchains):
    """
    Renderiza el formulario para editar una Toolchain existente (si hay una en edición).
    Maneja cambios dinámicos en el número de pasos de forma reactiva.
    """
    if "edit_toolchain" not in st.session_state:
        return

    target_name = st.session_state.edit_toolchain
    selected = tc_controller.get_toolchain_view(target_name)
    if not selected:
        st.error(f"No se encontró la Toolchain '{target_name}' para editar.")
        # Limpiar el estado si la toolchain ya no existe
        tc_controller.clear_toolchain_to_edit()
        return

    # Estado único por Toolchain
    step_key = f"edit_tc_num_steps_{target_name}"

    if step_key not in st.session_state:
        st.session_state[step_key] = len(selected.steps)

    # Callback para restaurar valores originales
    def clear_edit_form():
        # Resetear número de pasos al original
        st.session_state[step_key] = len(selected.steps)
        # Restaurar valores originales
        for i, step in enumerate(selected.steps):
            if i < 10:  # Límite razonable
                # Restaurar nombre de herramienta
                key_tool = f"edit_tool_{i}"
                if key_tool in st.session_state:
                    st.session_state[key_tool] = step.tool_name
                
                # Restaurar mapeo de inputs
                key_map = f"edit_map_{i}"
                if key_map in st.session_state:
                    map_text = "\n".join([f"{k}:{v}" for k, v in step.input_map.items()])
                    st.session_state[key_map] = map_text
        
        # Restaurar nombre y descripción
        if "edit_tc_name" in st.session_state:
            st.session_state.edit_tc_name = selected.name
        if "edit_tc_desc" in st.session_state:
            st.session_state.edit_tc_desc = selected.description
    
    # Callback para cancelar edición
    def cancel_edit_form():
        # Usar el controlador para limpiar el estado
        tc_controller.clear_toolchain_to_edit()
        st.rerun()
    
    # Callback para guardar cambios
    def save_edited_toolchain():
        # Recolectar los valores actuales de nombre, descripción y los pasos raw del formulario
        current_name = st.session_state.get(f"edit_tc_name_{target_name}", selected.name)
        current_desc = st.session_state.get(f"edit_tc_desc_{target_name}", selected.description)
        
        current_raw_steps = []
        for i in range(st.session_state[step_key]):
            tool_name_val = st.session_state.get(f"edit_tool_{target_name}_{i}", "")
            map_text_val = st.session_state.get(f"edit_map_{target_name}_{i}", "")
            current_raw_steps.append((tool_name_val, map_text_val))
            
        # Llamar al controlador con los datos crudos
        tc_controller.handle_save_edited_toolchain(
            original_name=target_name, # Pasar el nombre original
            new_name=current_name,
            new_description=current_desc,
            raw_steps=current_raw_steps
        )
        # La lógica de éxito/error y limpieza de estado la maneja el controlador
        # Podríamos añadir un rerun aquí si el controlador no lo hace
        st.rerun() # Añadido para asegurar refresco después de guardar

    # Sección de edición
    with st.expander(f"✏️ Editando Toolchain: {target_name}", expanded=True):
        st.markdown("### 🔄 Edición de Toolchain")
        st.markdown("### 🔢 Configuración de pasos")
        st.session_state[step_key] = st.number_input(
            label="Cantidad de pasos",
            min_value=1,
            max_value=10,
            value=st.session_state[step_key], # Usar el valor actual
            step=1,
            key=f"editor_num_steps_{target_name}" # Clave única para el number_input
        )

        # Título del formulario
        st.markdown(f"### 🔧 Editando: {selected.name}")

        # Campos de nombre y descripción con claves corregidas
        new_name = st.text_input(
            "Nombre", 
            key=f"edit_tc_name_{target_name}", 
            value=st.session_state.get(f"edit_tc_name_{target_name}", selected.name)
        )
        new_desc = st.text_area(
            "Descripción", 
            key=f"edit_tc_desc_{target_name}",
            value=st.session_state.get(f"edit_tc_desc_{target_name}", selected.description)
            )

        st.markdown("**Pasos de la Toolchain**")
        raw_steps = []
        for i in range(st.session_state[step_key]):
            # Usar claves con sufijo también para los pasos
            step_tool_key = f"edit_tool_{target_name}_{i}"
            step_map_key = f"edit_map_{target_name}_{i}"

            # Inicializar si es necesario (cuando se añaden pasos)
            if step_tool_key not in st.session_state:
                 st.session_state[step_tool_key] = ""
            if step_map_key not in st.session_state:
                 st.session_state[step_map_key] = ""
                 
            st.markdown(f"**Paso {i + 1}**")
            tool_name = st.text_input(f"Tool del Paso {i + 1}", key=step_tool_key)
            map_text = st.text_area(
                f"Input map (clave:valor por línea)",
                key=step_map_key,
                placeholder="Ejemplo:\ntexto: resumen\nidioma: idioma_destino"
            )
            # Recolectar los valores actuales de los inputs para pasar al controlador
            raw_steps.append((tool_name, map_text))
    
    # Botones fuera del formulario si usamos reactividad directa
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        st.button("💾 Guardar Cambios", key=f"save_edit_{target_name}", on_click=save_edited_toolchain, disabled=not new_name)
    with col2:
        st.button("🔄 Restaurar", key=f"reset_edit_{target_name}", on_click=clear_edit_form) # Renombrado para claridad
    with col3:
        st.button("❌ Cancelar Edición", key=f"cancel_edit_{target_name}", on_click=cancel_edit_form)

def render_ai_creator():
    """
    Generación asistida por IA de una Toolchain a partir de descripción en lenguaje natural.
    """
    with st.expander("🤖 Generar Toolchain con IA", expanded=False):
        # Callback para limpiar el formulario
        def clear_ui_ai_form():
            if "tc_ai_description" in st.session_state:
                st.session_state.tc_ai_description = ""
            if "generated_toolchain" in st.session_state:
                del st.session_state.generated_toolchain
            if "generation_error" in st.session_state:
                 del st.session_state.generation_error

        # Callback para generar toolchain
        def generate_toolchain_callback():
            # El controlador ahora maneja la obtención de API key y config
            # y almacena el resultado/error en session_state
            description = st.session_state.get("tc_ai_description", "")
            if description:
                with st.spinner("Generando Toolchain con IA..."):
                    tc_controller.handle_generate_toolchain_ai(description)
            else:
                st.warning("Por favor, introduce una descripción para la IA.")

        # Callback para guardar toolchain generada
        def save_generated_toolchain():
            # Llamar al controlador para guardar
            if "generated_toolchain" in st.session_state and st.session_state.generated_toolchain:
                tc_controller.handle_save_generated_toolchain(st.session_state.generated_toolchain)
            else:
                st.warning("No hay toolchain generada para guardar.")

        st.markdown("### Generación de Toolchain con IA")
        
        # Inicializar descripción en el estado si no existe
        if "tc_ai_description" not in st.session_state:
            st.session_state.tc_ai_description = ""
            
        st.markdown("Describe en lenguaje natural qué debe hacer la Toolchain")
        descripcion = st.text_area(
            "Descripción (prompt para IA)", 
            key="tc_ai_description",
            placeholder="Ej: Resume un texto y tradúcelo al francés"
        )

        # Botones de acción
        col1, col2 = st.columns(2)
        with col1:
            st.button("✨ Generar Toolchain", key="generar_toolchain",
                      on_click=generate_toolchain_callback,
                      disabled=not descripcion)
        with col2:
            st.button("🧹 Limpiar Campos", key="limpiar_ai_campos", on_click=clear_ui_ai_form)

        # Mostrar error de generación si existe
        if "generation_error" in st.session_state and st.session_state.generation_error:
            st.error(f"❌ Error generando: {st.session_state.generation_error}")

        # Mostrar resultado si hay Toolchain generada
        if "generated_toolchain" in st.session_state:
            generated_data = st.session_state.generated_toolchain
            if generated_data:
                st.success("✅ Toolchain generada por IA:")
                st.json(generated_data)

                # Botones para gestionar la toolchain generada
                col_save, col_discard = st.columns(2)
                with col_save:
                    st.button("💾 Guardar Toolchain Generada", key="guardar_toolchain_generada",
                              on_click=save_generated_toolchain)
                with col_discard:
                    # Usar la limpieza de UI que también limpia el resultado generado
                    st.button("❌ Descartar Generación", key="descartar_generada", on_click=clear_ui_ai_form)

def render_toolchain_modals(toolchains):
    """
    Confirmaciones de eliminación o ediciones futuras
    """
    if "delete_toolchain" in st.session_state:
        name = st.session_state.delete_toolchain
        st.warning(f"¿Eliminar la Toolchain `{name}` permanentemente?")
        col1, col2 = st.columns(2)
        with col1:
            # Llamar al controlador para eliminar
            if st.button("✅ Confirmar eliminación", key=f"confirm_delete_{name}"):
                tc_controller.handle_delete_toolchain(name)
                st.rerun() # Forzar refresco después de la acción
        with col2:
            # Llamar al controlador para limpiar el estado de eliminación
            if st.button("❌ Cancelar eliminación", key=f"cancel_delete_{name}"):
                tc_controller.clear_toolchain_to_delete()
                st.rerun()