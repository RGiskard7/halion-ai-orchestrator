from typing import Dict, Optional, Union
import requests

def fetch_instant_answer(query: str) -> Dict[str, str]:
    """
    Retrieves quick answers like definitions or facts directly from DuckDuckGo.

    Args:
        query (str): The search query.

    Returns:
        Dict[str, str]: A dictionary containing the query and the answer.

    Raises:
        ValueError: If the query is empty.
        Exception: If there is any issue with the request.
    """
    if not query:
        raise ValueError("Query cannot be empty.")

    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json"}

    try:
        response = requests.get(url, params=params)
        return {
            "query": query,
            "answer": response.json().get("AbstractText", "No instant answer available.")
        }
    except Exception as e:
        raise Exception(f"Error in fetch_instant_answer: {e}")

schema = {
    "name": "fetch_instant_answer",
    "description": "Fetches instant answers from DuckDuckGo.",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query."
            }
        },
        "required": ["query"]
    }
}
