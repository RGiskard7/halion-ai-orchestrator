# Archivo de prueba de diagnóstico
def test_diagnostico(mensaje="Prueba"):
    """Función de prueba para diagnóstico de escritura"""
    return f"Test completado: {mensaje}"
    
schema = {
    "name": "test_diagnostico",
    "description": "Herramienta de prueba para diagnosticar problemas de escritura",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "mensaje": {
                "type": "string",
                "description": "Mensaje de prueba"
            }
        },
        "required": []
    }
}
