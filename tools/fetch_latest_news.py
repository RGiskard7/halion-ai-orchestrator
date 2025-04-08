from typing import Dict, Optional, Union
import requests

def fetch_latest_news(country: str = 'us') -> Dict[str, Union[str, int]]:
    """
    Fetches the latest news from NewsAPI for a specific country.

    Args:
        country (str, optional): The country for which to fetch the news. Defaults to 'us'.

    Returns:
        Dict[str, Union[str, int]]: A dictionary containing the status of the request and the articles.

    Raises:
        Exception: If the request to the NewsAPI fails.
    """
    # Validate country
    if not isinstance(country, str):
        raise ValueError("Country must be a string")

    try:
        # Fetch news
        response = requests.get(f"https://newsapi.org/v2/top-headlines?country={country}")

        # Check if request was successful
        if response.status_code != 200:
            raise Exception(f"Error fetching news: {response.status_code}")

        return response.json()
    except Exception as e:
        raise Exception(f"Error in fetch_latest_news: {e}")

schema = {
    "name": "fetch_latest_news",
    "description": "Fetches the latest news for a specific country from NewsAPI",
    "postprocess": False,
    "parameters": {
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "The country for which to fetch the news"
            }
        },
        "required": ["country"]
    }
}
