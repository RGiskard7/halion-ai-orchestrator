# app/views/toolchains_view.py

import streamlit as st
import os
import json
from app.models.toolchain_model import Toolchain, ToolchainStep
from app.core.toolchain_loader import load_toolchains_from_file, TOOLCHAINS_FILE
from app.controllers.toolchain_executor import execute_toolchain
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

            if st.button("▶️ Lanzar Toolchain", key=f"launch_{selected.name}"):
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

        # Formulario de creación
        with st.form("form_nueva_toolchain"):
            name = st.text_input("Nombre único de la Toolchain")
            desc = st.text_area("Descripción")

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

            submitted = st.form_submit_button("💾 Guardar Toolchain")
            if submitted:
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
                    del st.session_state.new_tc_steps
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al guardar la Toolchain: {str(e)}")

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

    # Sección de edición
    with st.expander(f"✏️ Editando Toolchain: {target_name}", expanded=True):
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

        # Formulario de edición
        with st.form("form_edit_toolchain"):
            name = st.text_input("Nuevo nombre de la Toolchain", value=selected.name)
            desc = st.text_area("Descripción", value=selected.description)

            edited_steps = []
            for i in range(num_steps):
                if i < len(selected.steps):
                    existing_step = selected.steps[i]
                    default_tool = existing_step.tool_name
                    default_map = "\n".join([f"{k}:{v}" for k, v in existing_step.input_map.items()])
                else:
                    default_tool = ""
                    default_map = ""

                st.markdown(f"**Paso {i + 1}**")
                tool_name = st.text_input(f"Tool del Paso {i + 1}", value=default_tool, key=f"edit_tool_{i}")
                map_text = st.text_area(
                    f"Input map (clave:valor por línea)",
                    value=default_map,
                    key=f"edit_map_{i}",
                    placeholder="Ejemplo:\ntexto: resumen\nidioma: idioma_destino"
                )
                edited_steps.append((tool_name, map_text))

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar cambios")
            with col2:
                cancel = st.form_submit_button("❌ Cancelar")

        if submitted:
            try:
                steps = []
                for tool_name, raw_map in edited_steps:
                    input_map = {}
                    for line in raw_map.strip().splitlines():
                        if ':' in line:
                            k, v = line.split(':', 1)
                            input_map[k.strip()] = v.strip()
                    steps.append(ToolchainStep(tool_name=tool_name.strip(), input_map=input_map))

                updated = Toolchain(name=name.strip(), description=desc.strip(), steps=steps)

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
                del st.session_state.edit_toolchain
                del st.session_state[step_key]
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al actualizar la Toolchain: {str(e)}")

        if cancel:
            del st.session_state.edit_toolchain
            if step_key in st.session_state:
                del st.session_state[step_key]
            st.rerun()

def render_ai_creator():
    """
    Generación asistida por IA de una Toolchain a partir de descripción en lenguaje natural.
    """
    with st.expander("🤖 Generar Toolchain con IA", expanded=False):
        st.markdown("Describe en lenguaje natural qué debe hacer la Toolchain")
        descripcion = st.text_area("Descripción (prompt para IA)", placeholder="Ej: Resume un texto y tradúcelo al francés")

        if st.button("✨ Generar Toolchain con IA", disabled=not descripcion):
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
                        descripcion,
                        api_key,
                        model=model_config["model"],
                        temperature=model_config["temperature"]
                    )

                    # Mostrar resultado en la UI
                    st.session_state.generated_toolchain = toolchain_json
                    st.success("✅ Toolchain generada")
                    st.json(toolchain_json)

                except Exception as e:
                    st.error(f"❌ Error generando la Toolchain: {str(e)}")

        # Mostrar botón de guardar si hay Toolchain generada
        if "generated_toolchain" in st.session_state:
            toolchain = st.session_state.generated_toolchain
            if st.button("💾 Guardar Toolchain generada"):
                try:
                    if os.path.exists(TOOLCHAINS_FILE):
                        with open(TOOLCHAINS_FILE, "r") as f:
                            existing = json.load(f)
                    else:
                        existing = []

                    existing.append(toolchain)
                    with open(TOOLCHAINS_FILE, "w") as f:
                        json.dump(existing, f, indent=2, ensure_ascii=False)

                    st.success(f"✅ Toolchain `{toolchain['name']}` guardada correctamente.")
                    del st.session_state.generated_toolchain
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al guardar Toolchain generada: {str(e)}")

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