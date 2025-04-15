# app/views/toolchains_view.py

import streamlit as st
import os
import json
from app.models.toolchain_model import Toolchain, ToolchainStep
from app.core.toolchain_loader import load_toolchains_from_file, TOOLCHAINS_FILE
from app.core.tool_manager import get_tools
import time

def render():
    """
    Renderiza la vista completa de gestión de Toolchains
    """
    st.subheader("🔁 Gestión de Toolchains")

    # Recarga desde archivo
    toolchains = load_toolchains_from_file()

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
    render_ai_creator()  # Placeholder por ahora
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
            with col2:
                if st.button("▶️ Ejecutar", key=f"exec_{tc.name}"):
                    st.session_state.run_toolchain = tc.name
                if st.button("✏️ Editar", key=f"edit_{tc.name}"):
                    st.session_state.edit_toolchain = tc.name
                if st.button("🗑️ Borrar", key=f"delete_{tc.name}"):
                    st.session_state.delete_toolchain = tc.name

    # Ver si se quiere ejecutar
    if "run_toolchain" in st.session_state:
        selected = next((t for t in toolchains if t.name == st.session_state.run_toolchain), None)
        if selected:
            st.markdown("---")
            st.markdown(f"### 🚀 Ejecutar Toolchain: `{selected.name}`")

            initial_keys = set()
            for step in selected.steps:
                initial_keys.update(step.input_map.values())

            inputs = {}
            for k in sorted(initial_keys):
                inputs[k] = st.text_input(f"Input: {k}", key=f"input_{selected.name}_{k}")

            col1, col2 = st.columns(2)
            with col1:
                launch = st.button("▶️ Lanzar Toolchain", key=f"launch_{selected.name}")
            with col2:
                cancel = st.button("❌ Cancelar", key=f"cancel_run_{selected.name}")

            if cancel:
                del st.session_state.run_toolchain
                st.rerun()

            if launch:
                try:
                    tools = get_tools()
                    context = inputs.copy()

                    st.markdown("## 🧪 Ejecución paso a paso")
                    for i, step in enumerate(selected.steps):
                        st.markdown(f"### 🔹 Paso {i + 1}: `{step.tool_name}`")

                        inputs_for_step = {
                            param: context.get(source_key, None)
                            for param, source_key in step.input_map.items()
                        }

                        st.markdown("**Inputs:**")
                        st.json(inputs_for_step)

                        func = tools.get(step.tool_name, {}).get("func")
                        if not func:
                            st.error(f"❌ La herramienta `{step.tool_name}` no está disponible.")
                            break

                        try:
                            t0 = time.time()
                            output = func(**inputs_for_step)
                            t1 = time.time()
                            duration = t1 - t0

                            if not isinstance(output, dict):
                                output = {"result": output}

                            context.update(output)

                            st.success(f"✅ Ejecutado correctamente en {duration:.2f} segundos")
                            st.markdown("**Output:**")
                            st.json(output)

                        except Exception as e:
                            st.error(f"❌ Error al ejecutar `{step.tool_name}`: {str(e)}")
                            break

                    st.markdown("---")
                    st.markdown("## 🧾 Resultado final")
                    st.json(context)

                    del st.session_state.run_toolchain

                except Exception as e:
                    st.error(f"❌ Error general en la ejecución: {str(e)}")

def render_manual_creator():
    """
    Formulario de creación manual de nuevas toolchains, con actualización dinámica de pasos.
    """
    with st.expander("✏️ Crear Toolchain Manualmente", expanded=False):
        # Callback para limpiar el formulario
        def clear_manual_form():
            # Resetear número de pasos
            st.session_state.new_tc_steps = 1
            # Limpiar todos los campos de pasos
            for i in range(10):  # Usar un máximo razonable
                if f"new_tool_{i}" in st.session_state:
                    st.session_state[f"new_tool_{i}"] = ""
                if f"new_map_{i}" in st.session_state:
                    st.session_state[f"new_map_{i}"] = ""
            # Limpiar nombre y descripción si existen
            if "new_tc_name" in st.session_state:
                st.session_state.new_tc_name = ""
            if "new_tc_desc" in st.session_state:
                st.session_state.new_tc_desc = ""
        
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

        # Definir callback para guardar
        def save_toolchain_callback():
            try:
                steps = []
                for tool_name, raw_map in raw_steps:
                    input_map = {}
                    for line in raw_map.strip().splitlines():
                        if ':' in line:
                            k, v = line.split(':', 1)
                            input_map[k.strip()] = v.strip()
                    steps.append(ToolchainStep(tool_name=tool_name.strip(), input_map=input_map))

                nueva = Toolchain(name=name.strip(), description=desc.strip(), steps=steps)

                if os.path.exists(TOOLCHAINS_FILE):
                    with open(TOOLCHAINS_FILE, "r") as f:
                        existing = json.load(f)
                else:
                    existing = []

                existing.append({
                    "name": nueva.name,
                    "description": nueva.description,
                    "steps": [
                        {"tool_name": s.tool_name, "input_map": s.input_map}
                        for s in nueva.steps
                    ]
                })

                with open(TOOLCHAINS_FILE, "w") as f:
                    json.dump(existing, f, indent=2, ensure_ascii=False)

                st.success(f"✅ Toolchain `{nueva.name}` guardada correctamente.")
                clear_manual_form()
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al guardar la Toolchain: {str(e)}")
                
        # Botones con callbacks
        col1, col2 = st.columns(2)
        with col1:
            st.button("💾 Guardar Toolchain", key="guardar_toolchain", on_click=save_toolchain_callback, disabled=not name)
        with col2:
            st.button("🧹 Limpiar Campos", key="limpiar_campos_toolchain", on_click=clear_manual_form)

def render_toolchain_editor(toolchains):
    """
    Renderiza el formulario para editar una Toolchain existente (si hay una en edición).
    Maneja cambios dinámicos en el número de pasos de forma reactiva.
    """
    if "edit_toolchain" not in st.session_state:
        return

    target_name = st.session_state.edit_toolchain
    selected = next((t for t in toolchains if t.name == target_name), None)

    if not selected:
        st.error(f"No se encontró la Toolchain `{target_name}`.")
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
        del st.session_state.edit_toolchain
        if step_key in st.session_state:
            del st.session_state[step_key]
        # Limpiar campos adicionales
        for key in ["edit_tc_name", "edit_tc_desc"]:
            if key in st.session_state:
                del st.session_state[key]
        # Limpiar campos de pasos
        for i in range(10):
            for prefix in ["edit_tool_", "edit_map_"]:
                key = f"{prefix}{i}"
                if key in st.session_state:
                    del st.session_state[key]
        st.rerun()
    
    # Callback para guardar cambios
    def save_edited_toolchain():
        try:
            edited_steps = []
            for i in range(st.session_state[step_key]):
                key_tool = f"edit_tool_{i}"
                key_map = f"edit_map_{i}"
                
                if key_tool in st.session_state and key_map in st.session_state:
                    tool_name = st.session_state[key_tool]
                    raw_map = st.session_state[key_map]
                    
                    input_map = {}
                    for line in raw_map.strip().splitlines():
                        if ':' in line:
                            k, v = line.split(':', 1)
                            input_map[k.strip()] = v.strip()
                    
                    edited_steps.append(ToolchainStep(tool_name=tool_name.strip(), input_map=input_map))
                
            updated = Toolchain(
                name=st.session_state.edit_tc_name.strip(), 
                description=st.session_state.edit_tc_desc.strip(), 
                steps=edited_steps
            )

            # Reemplazar en archivo
            updated_data = []
            for t in toolchains:
                if t.name == target_name:
                    updated_data.append({
                        "name": updated.name,
                        "description": updated.description,
                        "steps": [
                            {"tool_name": s.tool_name, "input_map": s.input_map}
                            for s in updated.steps
                        ]
                    })
                else:
                    updated_data.append({
                        "name": t.name,
                        "description": t.description,
                        "steps": [
                            {"tool_name": s.tool_name, "input_map": s.input_map}
                            for s in t.steps
                        ]
                    })

            with open(TOOLCHAINS_FILE, "w") as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)

            st.success(f"✅ Toolchain `{updated.name}` actualizada correctamente.")
            cancel_edit_form()  # Limpiar y cerrar

        except Exception as e:
            st.error(f"❌ Error al actualizar la Toolchain: {str(e)}")
            
    # Sección de edición
    with st.expander(f"✏️ Editando Toolchain: {target_name}", expanded=True):
        st.markdown("### 🔄 Edición de Toolchain")
        st.markdown("### 🔢 Configuración de pasos")
        st.session_state[step_key] = st.number_input(
            label="Cantidad de pasos",
            min_value=1,
            max_value=10,
            value=st.session_state[step_key],
            step=1,
            key=f"input_steps_{target_name}"
        )

        num_steps = st.session_state[step_key]

        # Inicializar valores por defecto para el formulario
        if "edit_tc_name" not in st.session_state:
            st.session_state.edit_tc_name = selected.name
        if "edit_tc_desc" not in st.session_state:
            st.session_state.edit_tc_desc = selected.description
        
        # Campos de edición directamente (sin st.form)
        name = st.text_input("Nuevo nombre de la Toolchain", key="edit_tc_name")
        desc = st.text_area("Descripción", key="edit_tc_desc")

        for i in range(num_steps):
            # Preparar valores por defecto
            if i < len(selected.steps):
                existing_step = selected.steps[i]
                default_tool = existing_step.tool_name
                default_map = "\n".join([f"{k}:{v}" for k, v in existing_step.input_map.items()])
                # Inicializar estado si no existe
                key_tool = f"edit_tool_{i}"
                key_map = f"edit_map_{i}"
                if key_tool not in st.session_state:
                    st.session_state[key_tool] = default_tool
                if key_map not in st.session_state:
                    st.session_state[key_map] = default_map
            else:
                # Para pasos nuevos
                key_tool = f"edit_tool_{i}"
                key_map = f"edit_map_{i}"
                if key_tool not in st.session_state:
                    st.session_state[key_tool] = ""
                if key_map not in st.session_state:
                    st.session_state[key_map] = ""

            st.markdown(f"**Paso {i + 1}**")
            st.text_input(f"Tool del Paso {i + 1}", key=key_tool)
            st.text_area(
                f"Input map (clave:valor por línea)",
                key=key_map,
                placeholder="Ejemplo:\ntexto: resumen\nidioma: idioma_destino"
            )

        # Botones con callbacks
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("💾 Guardar", key="guardar_edit_toolchain", on_click=save_edited_toolchain, disabled=not name)
        with col2:
            st.button("🧹 Restaurar Valores", key="restaurar_edit_toolchain", on_click=clear_edit_form)
        with col3:
            st.button("❌ Cancelar", key="cancelar_edit_toolchain", on_click=cancel_edit_form)

def render_ai_creator():
    """
    Generación asistida por IA de una Toolchain a partir de descripción en lenguaje natural.
    """
    with st.expander("🤖 Generar Toolchain con IA", expanded=False):
        # Callback para limpiar el formulario
        def clear_ai_form():
            if "tc_ai_description" in st.session_state:
                st.session_state.tc_ai_description = ""
            if "generated_toolchain" in st.session_state:
                del st.session_state.generated_toolchain
        
        # Callback para generar toolchain
        def generate_toolchain_callback():
            api_key = st.session_state.get("api_key", "")
            if not api_key:
                st.error("❌ No hay API key configurada")
                return

            model_config = st.session_state.get("model_config", {
                "model": "gpt-4",
                "temperature": 0.7
            })

            with st.spinner("Generando Toolchain con IA..."):
                try:
                    from app.utils.ai_generation import generate_toolchain_with_ai
                    toolchain_json = generate_toolchain_with_ai(
                        st.session_state.tc_ai_description,
                        api_key,
                        model=model_config["model"],
                        temperature=model_config["temperature"]
                    )

                    # Mostrar resultado en la UI
                    st.session_state.generated_toolchain = toolchain_json
                    st.success("✅ Toolchain generada")
                    
                except Exception as e:
                    st.error(f"❌ Error generando la Toolchain: {str(e)}")
        
        # Callback para guardar toolchain generada
        def save_generated_toolchain():
            try:
                toolchain = st.session_state.generated_toolchain
                if os.path.exists(TOOLCHAINS_FILE):
                    with open(TOOLCHAINS_FILE, "r") as f:
                        existing = json.load(f)
                else:
                    existing = []

                existing.append(toolchain)
                with open(TOOLCHAINS_FILE, "w") as f:
                    json.dump(existing, f, indent=2, ensure_ascii=False)

                st.success(f"✅ Toolchain `{toolchain['name']}` guardada correctamente.")
                clear_ai_form()
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al guardar Toolchain generada: {str(e)}")
        
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
            st.button("🧹 Limpiar Campos", key="limpiar_ai_campos", on_click=clear_ai_form)

        # Mostrar resultado si hay Toolchain generada
        if "generated_toolchain" in st.session_state:
            toolchain = st.session_state.generated_toolchain
            st.json(toolchain)
            
            # Botones para gestionar la toolchain generada
            col1, col2 = st.columns(2)
            with col1:
                st.button("💾 Guardar Toolchain", key="guardar_toolchain_generada", 
                          on_click=save_generated_toolchain)
            with col2:
                st.button("❌ Descartar", key="descartar_generada", on_click=clear_ai_form)

def render_toolchain_modals(toolchains):
    """
    Confirmaciones de eliminación o ediciones futuras
    """
    if "delete_toolchain" in st.session_state:
        name = st.session_state.delete_toolchain
        st.warning(f"¿Eliminar la Toolchain `{name}` permanentemente?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirmar eliminación"):
                try:
                    new_data = [t for t in toolchains if t.name != name]
                    with open(TOOLCHAINS_FILE, "w") as f:
                        json.dump([
                            {
                                "name": t.name,
                                "description": t.description,
                                "steps": [
                                    {"tool_name": s.tool_name, "input_map": s.input_map}
                                    for s in t.steps
                                ]
                            }
                            for t in new_data
                        ], f, indent=2, ensure_ascii=False)
                    st.success(f"✅ Toolchain `{name}` eliminada.")
                    del st.session_state.delete_toolchain
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al eliminar: {str(e)}")
        with col2:
            if st.button("❌ Cancelar eliminación"):
                del st.session_state.delete_toolchain
                st.rerun()