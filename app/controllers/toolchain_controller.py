# app/controllers/toolchain_controller.py
import streamlit as st
from typing import Dict, List, Tuple, Optional
from app.models.toolchain_model import Toolchain, ToolchainStep
from app.core import toolchain_registry
from app.services import toolchain_service

# --- Funciones para obtener datos ---

def get_all_toolchains_view() -> List[Toolchain]:
    """
    Obtiene todas las toolchains del registro para la vista.
    Actualmente carga desde disco en cada llamada para reflejar cambios.
    TODO: Optimizar si la carga se vuelve lenta.
    """
    toolchains_dict = toolchain_registry.load_toolchains_from_disk()
    return list(toolchains_dict.values())

def get_toolchain_view(name: str) -> Toolchain | None:
    """
    Obtiene una toolchain específica por nombre desde el registro.
    """
    # Asegura que el registro está cargado/actualizado
    # Esta carga podría ser redundante si get_all_toolchains_view se llamó antes,
    # pero asegura que la toolchain individual esté actualizada si se accede directamente.
    toolchain_registry.load_toolchains_from_disk()
    return toolchain_registry.get_toolchain(name)

# --- Funciones para gestionar estado de la sesión (UI) ---

def set_toolchain_to_edit(name: str):
    """Marca una toolchain para ser editada en la UI."""
    st.session_state.edit_toolchain = name
    # Limpiar otros estados para evitar conflictos
    if "delete_toolchain" in st.session_state:
        del st.session_state.delete_toolchain
    if "run_toolchain" in st.session_state:
        del st.session_state.run_toolchain
    # Limpiar posible estado de generación AI
    if "generated_toolchain" in st.session_state:
         del st.session_state.generated_toolchain
    # Inicializar el número de pasos para el editor
    toolchain = get_toolchain_view(name)
    if toolchain:
        # Usar nombre único para la clave del número de pasos
        step_key = f"edit_tc_num_steps_{name}"
        st.session_state[step_key] = len(toolchain.steps)
        # Inicializar/Restaurar valores del formulario de edición
        # Nombre y descripción
        st.session_state[f"edit_tc_name_{name}"] = toolchain.name
        st.session_state[f"edit_tc_desc_{name}"] = toolchain.description
        # Pasos
        for i, step in enumerate(toolchain.steps):
             if i < 10: # Limitar para evitar demasiadas claves en session_state
                 st.session_state[f"edit_tool_{name}_{i}"] = step.tool_name
                 map_text = "\n".join([f"{k}:{v}" for k, v in step.input_map.items()])
                 st.session_state[f"edit_map_{name}_{i}"] = map_text


def clear_toolchain_to_edit():
    """Limpia el estado de edición de toolchain."""
    if "edit_toolchain" in st.session_state:
        target_name = st.session_state.edit_toolchain
        step_key = f"edit_tc_num_steps_{target_name}"
        # Limpiar claves de estado asociadas al editor
        if step_key in st.session_state:
            del st.session_state[step_key]
        # Claves de nombre y descripción
        for key in [f"edit_tc_name_{target_name}", f"edit_tc_desc_{target_name}"]:
             if key in st.session_state:
                 del st.session_state[key]
        # Claves de pasos (asumiendo un máximo de 10)
        for i in range(10):
             for prefix in [f"edit_tool_{target_name}_{i}", f"edit_map_{target_name}_{i}"]:
                 if prefix in st.session_state:
                     del st.session_state[prefix]

        del st.session_state.edit_toolchain


def set_toolchain_to_delete(name: str):
    """Marca una toolchain para ser eliminada en la UI."""
    st.session_state.delete_toolchain = name
    # Limpiar otros estados
    if "edit_toolchain" in st.session_state:
        clear_toolchain_to_edit() # Usar la función de limpieza
    if "run_toolchain" in st.session_state:
        clear_toolchain_to_run()


def clear_toolchain_to_delete():
    """Limpia el estado de eliminación de toolchain."""
    if "delete_toolchain" in st.session_state:
        del st.session_state.delete_toolchain

def set_toolchain_to_run(name: str):
    """Marca una toolchain para ser ejecutada en la UI."""
    st.session_state.run_toolchain = name
     # Limpiar otros estados
    if "edit_toolchain" in st.session_state:
        clear_toolchain_to_edit()
    if "delete_toolchain" in st.session_state:
        clear_toolchain_to_delete()

def clear_toolchain_to_run():
    """Limpia el estado de ejecución de toolchain."""
    if "run_toolchain" in st.session_state:
        # Limpiar inputs asociados a la ejecución si existen
        # Asumiendo un patrón como "input_{run_toolchain_name}_{key}"
        run_name = st.session_state.run_toolchain
        keys_to_delete = [k for k in st.session_state if k.startswith(f"input_{run_name}_")]
        for k in keys_to_delete:
            del st.session_state[k]
        del st.session_state.run_toolchain

# --- Funciones para manejar acciones (Crear, Actualizar, Eliminar) ---

def handle_save_new_toolchain(name: str, description: str, raw_steps: List[Tuple[str, str]]):
    """
    Procesa y guarda una nueva toolchain.
    Llamará a toolchain_registry.register_toolchain y toolchain_registry.save_toolchains_to_disk.
    Devuelve True si tiene éxito, False en caso contrario.
    """
    try:
        steps = []
        for i, (tool_name, raw_map) in enumerate(raw_steps):
            input_map = {}
            if not tool_name.strip():
                st.warning(f"Se omitió el Paso {i+1} porque no tiene nombre de herramienta.")
                continue # Saltar este paso si no hay nombre

            for line in raw_map.strip().splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    input_map[k.strip()] = v.strip()
                elif line.strip(): # Advertir sobre líneas mal formateadas que no están vacías
                     st.warning(f"Paso {i+1}, línea de mapeo ignorada (formato esperado 'clave:valor'): '{line}'")

            steps.append(ToolchainStep(tool_name=tool_name.strip(), input_map=input_map))

        if not steps:
             st.error("❌ No se puede guardar una toolchain sin pasos válidos.")
             return False
        if not name.strip():
             st.error("❌ La toolchain debe tener un nombre.")
             return False


        new_toolchain = Toolchain(name=name.strip(), description=description.strip(), steps=steps)

        # Cargar estado actual antes de añadir y guardar
        toolchain_registry.load_toolchains_from_disk()

        # Verificar si el nombre ya existe
        if toolchain_registry.get_toolchain(new_toolchain.name):
            st.error(f"❌ Ya existe una toolchain con el nombre '{new_toolchain.name}'.")
            return False

        toolchain_registry.register_toolchain(new_toolchain)

        if toolchain_registry.save_toolchains_to_disk():
            st.success(f"✅ Toolchain `{new_toolchain.name}` guardada correctamente.")
            # Limpiar estado del formulario de creación manual
            if "new_tc_name" in st.session_state: st.session_state.new_tc_name = ""
            if "new_tc_desc" in st.session_state: st.session_state.new_tc_desc = ""
            if "new_tc_steps" in st.session_state: st.session_state.new_tc_steps = 1
            for i in range(10): # Limpiar campos de pasos
                if f"new_tool_{i}" in st.session_state: st.session_state[f"new_tool_{i}"] = ""
                if f"new_map_{i}" in st.session_state: st.session_state[f"new_map_{i}"] = ""

            return True
        else:
            st.error("❌ Error al guardar las toolchains en el disco.")
            # Revertir registro en memoria sería ideal pero complejo aquí.
            return False

    except Exception as e:
        st.error(f"❌ Error procesando la Toolchain: {str(e)}")
        return False


def handle_save_edited_toolchain(original_name: str, new_name: str, new_description: str, raw_steps: List[Tuple[str, str]]):
    """
    Procesa y guarda los cambios de una toolchain editada.
    Gestiona la eliminación y el registro si el nombre cambia.
    Devuelve True si tiene éxito, False en caso contrario.
    """
    try:
        steps = []
        for i, (tool_name, raw_map) in enumerate(raw_steps):
            input_map = {}
            if not tool_name.strip():
                st.warning(f"Se omitió el Paso {i+1} durante la edición porque no tiene nombre de herramienta.")
                continue

            for line in raw_map.strip().splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    input_map[k.strip()] = v.strip()
                elif line.strip():
                    st.warning(f"Paso {i+1} (editado), línea de mapeo ignorada: '{line}'")

            steps.append(ToolchainStep(tool_name=tool_name.strip(), input_map=input_map))

        if not steps:
             st.error("❌ No se puede guardar una toolchain editada sin pasos válidos.")
             return False
        if not new_name.strip():
             st.error("❌ La toolchain editada debe tener un nombre.")
             return False

        updated_toolchain = Toolchain(name=new_name.strip(), description=new_description.strip(), steps=steps)

        # Cargar estado actual
        toolchain_registry.load_toolchains_from_disk()

        # Verificar si el nuevo nombre ya existe (y no es el nombre original)
        if original_name != updated_toolchain.name and toolchain_registry.get_toolchain(updated_toolchain.name):
            st.error(f"❌ Ya existe otra toolchain con el nombre '{updated_toolchain.name}'. No se puede renombrar.")
            return False

        # Si el nombre ha cambiado, eliminar el antiguo primero
        if original_name != updated_toolchain.name:
            if not toolchain_registry.delete_toolchain(original_name):
                 st.warning(f"No se encontró la toolchain original '{original_name}' al intentar renombrar. Se procederá a registrar la nueva.")

        # Registrar (o sobrescribir si el nombre no cambió)
        toolchain_registry.register_toolchain(updated_toolchain)

        if toolchain_registry.save_toolchains_to_disk():
            st.success(f"✅ Toolchain `{updated_toolchain.name}` actualizada correctamente.")
            # Limpiar estado de edición después de guardar con éxito
            clear_toolchain_to_edit()
            return True
        else:
            st.error("❌ Error al guardar las toolchains actualizadas en el disco.")
            # Intentar revertir cambios en memoria sería complejo.
            return False

    except Exception as e:
        st.error(f"❌ Error procesando la Toolchain editada: {str(e)}")
        return False


def handle_delete_toolchain(name: str):
    """
    Elimina una toolchain del registro y del disco.
    Devuelve True si tiene éxito, False en caso contrario.
    """
    try:
        # Cargar estado actual
        toolchain_registry.load_toolchains_from_disk()

        if toolchain_registry.delete_toolchain(name):
            if toolchain_registry.save_toolchains_to_disk():
                st.success(f"✅ Toolchain `{name}` eliminada correctamente.")
                clear_toolchain_to_delete() # Limpiar estado de eliminación
                return True
            else:
                st.error("❌ Error al guardar los cambios tras eliminar la toolchain del disco.")
                # Intentar restaurar en memoria? Complicado.
                return False
        else:
            # Si no estaba en el registro, puede que ya estuviera borrada o hubo un error previo.
            st.warning(f"La toolchain `{name}` no se encontró en el registro para eliminar.")
            clear_toolchain_to_delete() # Limpiar estado igualmente
            return False # Consideramos que no se completó la acción solicitada

    except Exception as e:
        st.error(f"❌ Error al eliminar la Toolchain: {str(e)}")
        return False


def handle_save_generated_toolchain(toolchain_data: Dict):
    """
    Guarda una toolchain generada por IA.
    Devuelve True si tiene éxito, False en caso contrario.
    """
    try:
        # Validar y crear objetos Toolchain/ToolchainStep
        steps_data = toolchain_data.get("steps", [])
        if not isinstance(steps_data, list):
             st.error("❌ Formato de pasos inválido en la toolchain generada.")
             return False

        steps = []
        for i, step_data in enumerate(steps_data):
             if not isinstance(step_data, dict):
                 st.error(f"❌ Formato inválido para el paso {i+1}.")
                 return False
             try:
                 # Validar campos mínimos
                 if "tool_name" not in step_data or not step_data["tool_name"]:
                      st.error(f"❌ Falta 'tool_name' o está vacío en el paso {i+1}.")
                      return False
                 if "input_map" not in step_data or not isinstance(step_data["input_map"], dict):
                      st.error(f"❌ Falta 'input_map' o no es un diccionario en el paso {i+1}.")
                      return False
                 steps.append(ToolchainStep(**step_data))
             except TypeError as te: # Captura errores si faltan keys o tienen tipos incorrectos
                  st.error(f"❌ Error al crear el paso {i+1} desde los datos generados: {te}")
                  return False

        tc_name = toolchain_data.get("name", f"Generated_Toolchain_{int(st.time.time())}").strip()
        tc_desc = toolchain_data.get("description", "").strip()

        if not tc_name:
             st.error("❌ La toolchain generada debe tener un nombre.")
             return False
        if not steps:
             st.error("❌ La toolchain generada no tiene pasos válidos.")
             return False

        new_toolchain = Toolchain(name=tc_name, description=tc_desc, steps=steps)

        # Cargar, registrar y guardar
        toolchain_registry.load_toolchains_from_disk()

        # Verificar si el nombre ya existe
        if toolchain_registry.get_toolchain(new_toolchain.name):
            st.error(f"❌ Ya existe una toolchain con el nombre generado '{new_toolchain.name}'.")
            # Podríamos intentar añadir un sufijo o pedir al usuario, pero por ahora fallamos.
            return False

        toolchain_registry.register_toolchain(new_toolchain)

        if toolchain_registry.save_toolchains_to_disk():
            st.success(f"✅ Toolchain generada `{new_toolchain.name}` guardada.")
            # Limpiar estado de generación AI
            if "generated_toolchain" in st.session_state:
                del st.session_state.generated_toolchain
            if "tc_ai_description" in st.session_state:
                 st.session_state.tc_ai_description = "" # Limpiar descripción
            return True
        else:
            st.error("❌ Error al guardar la toolchain generada en disco.")
            return False

    except Exception as e:
        st.error(f"❌ Error al procesar o guardar la toolchain generada: {str(e)}")
        return False

# --- Funciones relacionadas con servicios (Placeholders) ---

def handle_run_toolchain(name: str, inputs: Dict):
    """
    Orquesta la ejecución de una toolchain llamando al servicio.
    (A implementar cuando exista toolchain_service.py)
    """
    st.session_state.toolchain_run_result = None # Resetear resultado anterior
    st.session_state.toolchain_run_error = None
    st.session_state.toolchain_run_steps_log = [] # Log de pasos

    try:
        # Llamar al servicio real
        result, steps_log = toolchain_service.execute_toolchain(name, inputs)
        st.session_state.toolchain_run_result = result
        st.session_state.toolchain_run_steps_log = steps_log
        st.success(f"✅ Toolchain '{name}' ejecutada exitosamente.") # Mensaje de éxito
    except Exception as e:
        # Guardar el error para mostrarlo en la UI
        st.session_state.toolchain_run_error = str(e)
        st.error(f"❌ Error durante la ejecución de la toolchain '{name}': {e}") # Mostrar error

def handle_generate_toolchain_ai(description: str):
    """
    Orquesta la generación de una toolchain con IA llamando al servicio.
    Guarda el resultado en st.session_state.generated_toolchain o error en st.session_state.generation_error
    (A implementar cuando exista toolchain_service.py)
    """
    st.session_state.generated_toolchain = None # Resetear resultado anterior
    st.session_state.generation_error = None

    try:
        # Obtener API key y configuración del modelo desde el estado de la sesión
        api_key = st.session_state.get("api_key", "")
        model_config = st.session_state.get("model_config", {"model": "gpt-4", "temperature": 0.7}) # Usar defaults si no existe
        
        if not api_key:
            st.error("❌ Falta la API Key de OpenAI en la configuración para usar la generación AI.")
            st.session_state.generation_error = "API Key no configurada."
            return
            
        # Llamar al servicio real
        generated_data = toolchain_service.generate_toolchain_via_ai(description, api_key, model_config)
        st.session_state.generated_toolchain = generated_data
        # Podríamos añadir un mensaje de éxito, pero la UI se actualizará para mostrar los datos generados
        
    except Exception as e:
        # Guardar el error para mostrarlo en la UI
        st.session_state.generation_error = str(e)
        st.error(f"❌ Error durante la generación AI de la toolchain: {e}") # Mostrar error 