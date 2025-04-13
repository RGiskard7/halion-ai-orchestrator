from typing import Dict, Optional, Union
import requests
import os
import random
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def recommend_movie_by_genre(genre: str) -> Dict[str, Union[str, int]]:
    """
    Recomienda una película aleatoria del género especificado y proporciona información sobre ella.

    Args:
        genre (str): El género de la película que se desea buscar. 

    Returns:
        Dict[str, Union[str, int]]: Información de la película recomendada.

    Raises:
        ValueError: Si el parámetro 'genre' no es proporcionado o si la API key no está configurada.
    """

    # Obtener API key desde variables de entorno
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise ValueError("API key no configurada. Añade TMDB_API_KEY a las variables de entorno.")

    # Validar que se haya proporcionado un género
    if not genre:
        raise ValueError("El género no puede estar vacío")

    try:
        # Obtener la lista de películas del género especificado
        response = requests.get(f"https://api.themoviedb.org/3/genre/{genre}/movies?api_key={api_key}")
        response.raise_for_status()

        # Seleccionar una película aleatoria de la lista
        movies = response.json().get('results', [])
        if not movies:
            return {"message": "No se encontraron películas para el género proporcionado"}

        movie = random.choice(movies)
        
        # Devolver la información de la película
        return {
            "title": movie.get("title"),
            "overview": movie.get("overview"),
            "release_date": movie.get("release_date"),
            "vote_average": movie.get("vote_average"),
            "popularity": movie.get("popularity")
        }
    except Exception as e:
        raise Exception(f"Error en recommend_movie_by_genre: {e}")

schema = {
    "name": "recommend_movie_by_genre",
    "description": "Recomienda una película aleatoria del género especificado y proporciona información sobre ella.",
    "postprocess": False,
    "parameters": {
        "type": "object",
        "properties": {
            "genre": {
                "type": "string",
                "description": "El género de la película que se desea buscar."
            }
        },
        "required": ["genre"]
    }
}
