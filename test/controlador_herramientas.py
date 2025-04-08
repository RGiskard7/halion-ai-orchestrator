import os
import re
import json
import datetime
import streamlit as st
from dynamic_tool_registry import register_tool
from tool_manager import load_all_tools, set_tool_status

def crear_herramienta_desde_codigo(codigo: str, log_file: str = "debug_logs/creacion_directa.log"):
    """
    Función que crea una herramienta a partir del código generado por la IA.
    Esta es una versión simplificada y directa del controlador en streamlit_app.py.
    
    Args:
        codigo (str): El código de la herramienta a crear
        log_file (str): Archivo donde se registrará el proceso
    
    Returns:
        bool: True si la herramienta se creó correctamente, False en caso contrario
    """
    with open(log_file, "a") as log:
        log.write(f"\n\n--- NUEVA CREACIÓN DE HERRAMIENTA {datetime.datetime.now().isoformat()} ---\n")
        log.write(f"Longitud del código: {len(codigo)} caracteres\n")
        
        # 1. Extraer nombre de la función
        func_match = re.search(r'def\s+(\w+)', codigo)
        if not func_match:
            log.write("ERROR: No se pudo encontrar el nombre de la función\n")
            return False
        
        tool_name = func_match.group(1)
        log.write(f"Nombre de herramienta extraído: {tool_name}\n")
        
        # 2. Determinar ruta del archivo
        tools_path = os.path.join(os.getcwd(), "tools")
        file_path = os.path.join(tools_path, f"{tool_name}.py")
        log.write(f"Ruta absoluta del archivo: {file_path}\n")
        
        # 3. Verificar directorio
        if not os.path.exists(tools_path):
            log.write(f"Creando directorio tools: {tools_path}\n")
            os.makedirs(tools_path)
        
        # 4. Crear el archivo
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(codigo)
            
            exists = os.path.exists(file_path)
            log.write(f"¿Archivo creado?: {exists}\n")
            
            if exists:
                log.write(f"Tamaño del archivo: {os.path.getsize(file_path)} bytes\n")
                
                # 5. Activar la herramienta en el sistema
                set_tool_status(tool_name, True)
                log.write(f"Herramienta activada: {tool_name}\n")
                
                # 6. Recargar las herramientas
                log.write("Recargando todas las herramientas...\n")
                load_all_tools()
                
                log.write("✅ PROCESO COMPLETADO CON ÉXITO\n")
                return True
            else:
                log.write("❌ ERROR: No se pudo crear el archivo\n")
                return False
                
        except Exception as e:
            log.write(f"❌ ERROR: {str(e)}\n")
            import traceback
            log.write(f"TRACEBACK: {traceback.format_exc()}\n")
            return False


def interfaz_simplificada():
    """
    Interfaz Streamlit simplificada para probar la creación de herramientas
    """
    st.title("🔧 Controlador de Herramientas Simplificado")
    
    st.write("""
    Esta es una interfaz simplificada para diagnosticar problemas con la creación de herramientas.
    Si funciona aquí pero no en la aplicación principal, sabemos que el problema está en el proceso dentro de la aplicación.
    """)
    
    # Ejemplo de código de herramienta
    ejemplo_codigo = '''
def suma_numeros(a: int, b: int) -> int:
    """
    Suma dos números enteros.
    
    Args:
        a (int): Primer número
        b (int): Segundo número
        
    Returns:
        int: La suma de los dos números
    """
    return a + b

schema = {
    "name": "suma_numeros",
    "description": "Suma dos números enteros",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "a": {
                "type": "integer",
                "description": "Primer número"
            },
            "b": {
                "type": "integer",
                "description": "Segundo número"
            }
        },
        "required": ["a", "b"]
    }
}
'''
    
    codigo = st.text_area("Código de la herramienta", value=ejemplo_codigo, height=400)
    
    if st.button("Crear Herramienta"):
        with st.spinner("Creando herramienta..."):
            resultado = crear_herramienta_desde_codigo(codigo)
            
            if resultado:
                st.success("✅ Herramienta creada correctamente")
                st.write("Verificando si está disponible en el sistema...")
                
                # Obtener el nombre de la herramienta
                func_match = re.search(r'def\s+(\w+)', codigo)
                tool_name = func_match.group(1) if func_match else "desconocida"
                
                # Verificar si se puede importar
                try:
                    spec = __import__(f"tools.{tool_name}", fromlist=[tool_name])
                    st.success(f"✅ La herramienta '{tool_name}' se importó correctamente")
                except ImportError:
                    st.error(f"❌ No se pudo importar la herramienta '{tool_name}'")
            else:
                st.error("❌ Error al crear la herramienta. Revisa los logs para más detalles.")
                
                with open("debug_logs/creacion_directa.log", "r") as log:
                    lines = log.readlines()
                    if lines:
                        # Mostrar las últimas 20 líneas del log
                        st.code("".join(lines[-20:]))

if __name__ == "__main__":
    # Si ejecutamos este script directamente, mostramos la interfaz
    interfaz_simplificada() 