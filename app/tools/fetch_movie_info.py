from typing import Dict, List, Optional, Union
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def fetch_movie_info(movie_names: List[str]) -> Dict[str, Union[str, Dict]]:
    """
    Fetches information about the given movies from the OMDB database.

    Args:
        movie_names (List[str]): List of movie names for which the information is to be fetched

    Returns:
        Dict[str, Union[str, Dict]]: A dictionary where keys are movie names and values are dictionaries containing movie information.

    Raises:
        ValueError: If movie_names is empty or if the OMDB_API_KEY is not set in the environment variables.
    """
    # Obtener API key desde variables de entorno
    api_key = os.getenv("OMDB_API_KEY")
    if not api_key:
        raise ValueError("OMDB API key not set. Please set OMDB_API_KEY in the environment variables")

    if not movie_names:
        raise ValueError("movie_names cannot be empty")

    base_url = "http://www.omdbapi.com/"
    movies_info = {}

    for movie_name in movie_names:
        try:
            response = requests.get(base_url, params={"t": movie_name, "apikey": api_key})
            response.raise_for_status()
            movies_info[movie_name] = response.json()
        except Exception as e:
            raise Exception(f"Error while fetching information for {movie_name} from OMDB: {e}")

    return movies_info

schema = {
    "name": "fetch_movie_info",
    "description": "Fetches information about the given movies from the OMDB database.",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "movie_names": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of movie names for which the information is to be fetched"
            }
        },
        "required": ["movie_names"]
    }
}
