def saludar(nombre: str) -> str:
    return f"Hola, {nombre}, ¿cómo estás hoy?"

schema = {
    "name": "saludar",
    "description": "Saluda cordialmente a una persona por su nombre",
    "parameters": {
        "type": "object",
        "properties": {
            "nombre": {"type": "string", "description": "Nombre de la persona"}
        },
        "required": ["nombre"]
    }
}
