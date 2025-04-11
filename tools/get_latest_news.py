from typing import Dict, Optional, Union
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_latest_news(country: str) -> Dict[str, Union[str, int]]:
    """
    Obtiene las últimas noticias relevantes de un país especificado.

    Args:
        country (str): Código ISO del país (2 caracteres)

    Returns:
        Dict[str, Union[str, int]]: Diccionario con las últimas noticias

    Raises:
        ValueError: Si el país no tiene código ISO válido
    """
    # Obtener API key desde variables de entorno
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise ValueError("API key no configurada. Añade NEWS_API_KEY a las variables de entorno.")

    # Validaciones
    if not country or len(country) != 2:
        raise ValueError("El código de país debe ser un código ISO de 2 caracteres")

    try:
        # Lógica principal
        url = f"https://newsapi.org/v2/top-headlines?country={country}"
        headers = {"Authorization": api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error en get_latest_news: {e}")

schema = {
    "name": "get_latest_news",
    "description": "Obtiene las últimas noticias relevantes de un país especificado",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "Código ISO del país (2 caracteres)"
            }
        },
        "required": ["country"]
    }
}