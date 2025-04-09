from typing import Dict, Optional
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_movie_info(movie_title: str) -> Dict[str, Optional[str]]:
    """
    Get the information about a movie or TV series from the OMDB API and also 
    find out which platforms it is available on using the JustWatch API.
    
    Args:
        movie_title (str): The title of the movie or TV series.
    
    Returns:
        Dict[str, Optional[str]]: A dictionary containing the movie information, 
                                   or None if the movie was not found.
    
    Raises:
        ValueError: If the movie title is empty.
        Exception: If there was an error while fetching the movie information.
    """
    # Get API keys from environment variables
    omdb_api_key = os.getenv("OMDB_API_KEY")
    justwatch_api_key = os.getenv("JUSTWATCH_API_KEY")

    if not omdb_api_key:
        raise ValueError("OMDB API key not set. Please add OMDB_API_KEY to your environment variables.")
    if not justwatch_api_key:
        raise ValueError("JustWatch API key not set. Please add JUSTWATCH_API_KEY to your environment variables.")
    
    # Validate movie title
    if not movie_title:
        raise ValueError("The movie title cannot be empty.")
    
    try:
        # Fetch movie information from OMDB API
        omdb_response = requests.get(f"http://www.omdbapi.com/?apikey={omdb_api_key}&t={movie_title}")
        omdb_data = omdb_response.json()
        
        if omdb_data["Response"] == "False":
            return None
        
        # Fetch platform information from JustWatch API
        justwatch_response = requests.get(f"https://api.justwatch.com/content/titles/movie/{omdb_data['imdbID']}/locale/en_US?apikey={justwatch_api_key}")
        justwatch_data = justwatch_response.json()
        
        # Combine the movie information and platform information
        movie_info = omdb_data
        movie_info["Platforms"] = justwatch_data["offers"]
        
        return movie_info
    except Exception as e:
        raise Exception(f"Error while fetching movie information: {e}")

schema = {
    "name": "get_movie_info",
    "description": "Get the information about a movie or TV series and find out which platforms it is available on.",
    "postprocess": False,
    "parameters": {
        "type": "object",
        "properties": {
            "movie_title": {
                "type": "string",
                "description": "The title of the movie or TV series."
            }
        },
        "required": ["movie_title"]
    }
}
