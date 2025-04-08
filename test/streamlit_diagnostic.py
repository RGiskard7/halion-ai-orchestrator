import os
import sys
import re
import time
import streamlit as st

# Crear directorio de logs si no existe
debug_dir = "debug_logs"
if not os.path.exists(debug_dir):
    os.makedirs(debug_dir, exist_ok=True)

def escribir_log(mensaje):
    """Escribe un mensaje en el archivo de log de diagnóstico"""
    # Crear carpeta si no existe
    if not os.path.exists("debug_logs"):
        os.makedirs("debug_logs")
    with open("debug_logs/streamlit_diagnostic.log", "a") as f:
        f.write(f"{mensaje}\n")

def crear_herramienta(codigo):
    """
    Versión simplificada de la función que maneja el botón "Usar Esta Herramienta"
    """
    escribir_log("===== INICIO DE CREACIÓN DE HERRAMIENTA =====")
    escribir_log(f"Código recibido (longitud): {len(codigo)} caracteres")
    
    # Extraer el nombre de la función desde el código
    func_match = re.search(r'def\s+(\w+)', codigo)
    if not func_match:
        escribir_log("ERROR: No se pudo encontrar el nombre de la función en el código")
        return False, "No se pudo encontrar el nombre de la función en el código"
    
    tool_name = func_match.group(1)
    escribir_log(f"Nombre extraído: {tool_name}")
    
    # Ruta del archivo a crear
    tools_dir = os.path.join(os.getcwd(), "tools")
    file_path = os.path.join(tools_dir, f"{tool_name}.py")
    escribir_log(f"Ruta del archivo: {file_path}")
    
    # Verificar si el directorio existe
    if not os.path.exists(tools_dir):
        os.makedirs(tools_dir)
        escribir_log(f"Creado directorio: {tools_dir}")
        
    # Intentar escribir el archivo
    try:
        with open(file_path, "w") as f:
            f.write(codigo)
        
        escribir_log(f"Archivo creado exitosamente: {file_path}")
        escribir_log(f"Tamaño del archivo: {os.path.getsize(file_path)} bytes")
        
        return True, f"Herramienta '{tool_name}' creada exitosamente"
    except Exception as e:
        error_msg = f"ERROR al escribir el archivo: {str(e)}"
        escribir_log(error_msg)
        return False, error_msg

# Configuración de la página
st.set_page_config(
    page_title="Diagnóstico de Creación de Herramientas",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Diagnóstico de Creación de Herramientas")

st.markdown("""
Esta es una versión simplificada de la aplicación para diagnosticar el problema específico 
con la creación de herramientas con IA. Solo incluye el flujo problemático.
""")

# Código de ejemplo para la herramienta
ejemplo_codigo = '''
def contador_palabras(texto: str) -> dict:
    """
    Cuenta las palabras en un texto.
    
    Args:
        texto (str): El texto a analizar.
        
    Returns:
        dict: Diccionario con el conteo de palabras.
    """
    palabras = texto.lower().split()
    resultado = {}
    
    for palabra in palabras:
        # Eliminar puntuación
        palabra = palabra.strip('.,;:!?"\'()[]{}')
        if palabra:
            if palabra in resultado:
                resultado[palabra] += 1
            else:
                resultado[palabra] = 1
    
    return resultado

schema = {
    "name": "contador_palabras",
    "description": "Cuenta las palabras en un texto dado",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "texto": {
                "type": "string",
                "description": "El texto a analizar"
            }
        },
        "required": ["texto"]
    }
}
'''

# Mostrar la interfaz
codigo = st.text_area("Código de la herramienta", value=ejemplo_codigo, height=400)

# Paso 1: Generar código
if st.button("🔍 Generar Código"):
    escribir_log("Botón 'Generar Código' presionado")
    st.session_state.codigo_generado = codigo
    st.success("✅ Código generado. Ahora puedes usar el botón 'Usar Esta Herramienta'")
    
# Paso 2: Usar la herramienta
if 'codigo_generado' in st.session_state:
    st.write("---")
    st.write("**Código generado disponible para usar**")
    if st.button("✨ Usar Esta Herramienta"):
        escribir_log("Botón 'Usar Esta Herramienta' presionado")
        with st.spinner("Procesando..."):
            exito, mensaje = crear_herramienta(st.session_state.codigo_generado)
            
            if exito:
                st.success(mensaje)
            else:
                st.error(mensaje)
            
            # Mostrar logs
            with open("debug_logs/streamlit_diagnostic.log", "r") as log:
                st.code(log.read())

# Información de diagnóstico
with st.expander("ℹ️ Información del Sistema", expanded=False):
    st.write(f"**Directorio actual:** {os.getcwd()}")
    st.write(f"**Directorio de herramientas:** {os.path.join(os.getcwd(), 'tools')}")
    st.write(f"**Python version:** {sys.version}")
    st.write(f"**Streamlit version:** {st.__version__}")
    
    # Listar herramientas existentes
    tools_dir = os.path.join(os.getcwd(), "tools")
    if os.path.exists(tools_dir):
        st.write("**Herramientas existentes:**")
        for item in os.listdir(tools_dir):
            if item.endswith(".py"):
                st.write(f"- {item}") 