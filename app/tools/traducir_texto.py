def traducir_texto(texto, idioma):
    """
    Traducción simulada (no real). Devuelve el texto con una etiqueta de idioma.
    """
    return {"traduccion": f"[{idioma.upper()}] {texto}"}

schema = {
    "name": "traducir_texto",
    "description": "Traduce un texto a otro idioma (simulado)",
    "parameters": {
        "type": "object",
        "properties": {
            "texto": {
                "type": "string",
                "description": "Texto a traducir"
            },
            "idioma": {
                "type": "string",
                "description": "Idioma destino (ej: 'fr', 'en')"
            }
        },
        "required": ["texto", "idioma"]
    },
    "postprocess": False
}