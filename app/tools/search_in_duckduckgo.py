from typing import Dict, Optional, Union
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def search_in_duckduckgo(query: str, language: Optional[str] = "es") -> Dict[str, Union[str, int]]:
    """
    Realiza una búsqueda en internet a través de la API de DuckDuckGo.

    Args:
        query (str): El término de búsqueda. 
        language (str, optional): El idioma preferido para los resultados de la búsqueda. Por defecto es inglés ('en'). 

    Returns:
        Dict[str, Union[str, int]]: Un diccionario que contiene el estado de la respuesta y los resultados de la búsqueda.

    Raises:
        ValueError: Se lanza este error si no se proporciona la clave de API o si el término de búsqueda está vacío.
    """
    # Validaciones
    if not query:
        raise ValueError("El término de búsqueda no puede estar vacío")

    try:
        # Lógica principal
        url = f"https://api.duckduckgo.com/?q={query}&format=json&kl={language}"
        response = requests.get(url)
        return {
            "status": response.status_code,
            "results": response.json()
        }
    except Exception as e:
        raise Exception(f"Error en search_in_duckduckgo: {e}")

schema = {
    "name": "search_in_duckduckgo",
    "description": "Realiza una búsqueda en internet a través de la API de DuckDuckGo.",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "El término de búsqueda."
            },
            "language": {
                "type": "string",
                "description": "El idioma preferido para los resultados de la búsqueda. Por defecto es inglés ('en')."
            }
        },
        "required": ["query"]
    }
}
