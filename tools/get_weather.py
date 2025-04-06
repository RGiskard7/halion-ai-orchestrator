def get_weather(city: str) -> str:
    return f"El clima en {city} es soleado con 22°C."

schema = {
    "name": "get_weather",
    "description": "Obtiene el clima actual para una ciudad",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "Nombre de la ciudad"}
        },
        "required": ["city"]
    }
}
