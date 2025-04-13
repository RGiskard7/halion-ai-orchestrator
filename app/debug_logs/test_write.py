"""
Archivo de prueba para verificar que se puede escribir en el directorio app/debug_logs
"""

import os
import datetime

def test_write():
    """
    Función que escribe un mensaje de prueba en un archivo temporal
    para verificar que tenemos permisos de escritura en este directorio.
    """
    current_time = datetime.datetime.now().isoformat()
    
    # Obtener la ruta del directorio actual (app/debug_logs)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    test_content = f"""
    ===================================
    TEST DE ESCRITURA: {current_time}
    ===================================
    
    Este archivo se creó para verificar que se puede escribir en el directorio
    app/debug_logs. Si puedes ver este mensaje, significa que el directorio
    está configurado correctamente y tiene los permisos adecuados.
    
    Información adicional:
    - Ruta actual: {current_dir}
    - Contenido del directorio: {os.listdir(current_dir)}
    """
    
    # Ruta del archivo relativa al directorio actual
    file_path = os.path.join(current_dir, "test_write_result.txt")
    
    # Escribir el contenido en un archivo
    with open(file_path, "w") as f:
        f.write(test_content)
    
    return f"Prueba completada exitosamente. Archivo creado en: {file_path}"

if __name__ == "__main__":
    result = test_write()
    print(result) 