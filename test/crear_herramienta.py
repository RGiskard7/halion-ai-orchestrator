import os
import sys
import datetime
import json

def crear_herramienta_test():
    """
    Script de diagnóstico para crear una herramienta de prueba directamente,
    sin usar la interfaz Streamlit.
    """
    print("="*50)
    print("DIAGNÓSTICO DE CREACIÓN DE HERRAMIENTAS")
    print("="*50)
    print(f"Fecha y hora: {datetime.datetime.now().isoformat()}")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print("-"*50)
    
    # Prueba 1: Información del sistema de archivos
    print("\nPRUEBA 1: INFORMACIÓN DEL SISTEMA DE ARCHIVOS")
    tools_dir = os.path.join(os.getcwd(), "tools")
    print(f"Ruta de directorio tools: {tools_dir}")
    print(f"¿Existe directorio tools?: {os.path.exists(tools_dir)}")
    print(f"Permisos del directorio: {oct(os.stat(tools_dir).st_mode)[-3:]}")
    print(f"Usuario actual: {os.getlogin()}")
    
    if os.path.exists(tools_dir):
        print("\nContenido del directorio tools:")
        for item in os.listdir(tools_dir):
            item_path = os.path.join(tools_dir, item)
            if os.path.isfile(item_path):
                print(f"  - ARCHIVO: {item} ({os.path.getsize(item_path)} bytes)")
            else:
                print(f"  - DIR: {item}")
    
    # Prueba 2: Crear un archivo de prueba
    print("\nPRUEBA 2: CREAR ARCHIVO EN DIRECTORIO TOOLS")
    test_tool_path = os.path.join(tools_dir, "prueba_script.py")
    
    print(f"Intentando crear archivo: {test_tool_path}")
    
    # Contenido de la herramienta de prueba
    code = """
def prueba_script(texto="Hola mundo"):
    \"\"\"
    Herramienta de prueba creada por script de diagnóstico.
    
    Args:
        texto (str): Texto a devolver.
        
    Returns:
        str: Mensaje formateado.
    \"\"\"
    return f"Prueba exitosa: {texto}"

schema = {
    "name": "prueba_script",
    "description": "Herramienta de prueba creada por script de diagnóstico",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "texto": {
                "type": "string",
                "description": "Texto a devolver"
            }
        },
        "required": []
    }
}
"""
    
    try:
        with open(test_tool_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"¿Archivo creado?: {os.path.exists(test_tool_path)}")
        if os.path.exists(test_tool_path):
            print(f"Tamaño del archivo: {os.path.getsize(test_tool_path)} bytes")
            print("✅ PRUEBA EXITOSA: Archivo creado correctamente")
        else:
            print("❌ ERROR: El archivo no existe después de intentar crearlo")
    except Exception as e:
        print(f"❌ ERROR creando archivo: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    
    # Prueba 3: Verificar si Streamlit tiene permisos
    print("\nPRUEBA 3: VERIFICAR PERMISOS DE STREAMLIT")
    try:
        import streamlit
        print(f"Streamlit instalado: versión {streamlit.__version__}")
        print(f"Ubicación de Streamlit: {streamlit.__file__}")
        
        # Si estamos ejecutando con streamlit, intentar crear un archivo temporal
        if 'streamlit.runtime' in sys.modules:
            print("Ejecutando dentro de Streamlit runtime")
            temp_file = os.path.join(os.getcwd(), "streamlit_test.txt")
            with open(temp_file, "w") as f:
                f.write("Test desde Streamlit runtime")
            print(f"Archivo de prueba creado: {os.path.exists(temp_file)}")
        else:
            print("No estamos dentro del runtime de Streamlit")
    except ImportError:
        print("Streamlit no está instalado")
    except Exception as e:
        print(f"Error verificando Streamlit: {str(e)}")
    
    print("\n" + "="*50)
    print("DIAGNÓSTICO FINALIZADO")
    print("="*50)

if __name__ == "__main__":
    crear_herramienta_test() 