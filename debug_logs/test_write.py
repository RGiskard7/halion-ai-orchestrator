import os
import datetime

def test_file_writing():
    print("Script de prueba para escritura de archivos")
    print(f"Fecha y hora: {datetime.datetime.now().isoformat()}")
    print(f"Directorio actual: {os.getcwd()}")
    
    # Prueba 1: Escribir en el directorio actual
    try:
        with open("test_current_dir.txt", "w") as f:
            f.write("Prueba de escritura en directorio actual\n")
        print(f"¿Archivo creado en directorio actual? {os.path.exists('test_current_dir.txt')}")
    except Exception as e:
        print(f"Error al escribir en directorio actual: {str(e)}")
    
    # Prueba 2: Escribir en subdirectorio tools
    try:
        tools_path = os.path.join(os.getcwd(), "tools")
        file_path = os.path.join(tools_path, "test_tool.py")
        print(f"Ruta completa: {file_path}")
        print(f"¿Existe directorio tools? {os.path.exists(tools_path)}")
        
        with open(file_path, "w") as f:
            f.write("def test_tool():\n")
            f.write("    return 'Prueba de escritura OK'\n\n")
            f.write("schema = {\n")
            f.write('    "name": "test_tool",\n')
            f.write('    "description": "Herramienta de prueba",\n')
            f.write('    "postprocess": True,\n')
            f.write('    "parameters": {\n')
            f.write('        "type": "object",\n')
            f.write('        "properties": {},\n')
            f.write('        "required": []\n')
            f.write('    }\n')
            f.write('}\n')
        
        print(f"¿Archivo creado en tools? {os.path.exists(file_path)}")
        if os.path.exists(file_path):
            print(f"Tamaño del archivo: {os.path.getsize(file_path)}")
    except Exception as e:
        print(f"Error al escribir en tools: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_file_writing() 