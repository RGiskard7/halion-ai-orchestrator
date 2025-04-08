from typing import Dict, Optional, Union
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def fetch_relevant_news(country: str) -> Dict[str, Union[str, int]]:
    """
    Fetches the latest relevant news of a specified country from an API.

    Args:
        country (str): The country to fetch news for.

    Returns:
        Dict[str, Union[str, int]]: The latest relevant news for the country.
        
    Raises:
        ValueError: If the country is not specified or the API key is not set.
    """
    # Obtener API key desde variables de entorno
    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        raise ValueError("API key not configured. Add NEWS_API_KEY to environment variables.")
    
    # Validaciones
    if not country:
        raise ValueError("Country cannot be empty")
    
    try:
        response = requests.get(f"https://newsapi.org/v2/top-headlines?country={country}", headers={"Authorization": news_api_key})
        response.raise_for_status()
        news = response.json()
        return news
    except Exception as e:
        raise Exception(f"Error in fetching news: {e}")

schema = {
    "name": "fetch_relevant_news",
    "description": "Fetches the latest relevant news of a specified country.",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "The country to fetch news for."
            }
        },
        "required": ["country"]
    }
}
