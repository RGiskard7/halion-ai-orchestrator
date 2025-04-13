from typing import Dict, Optional, Union
import requests

def internet_search_tool(query: str, category: Optional[str] = None, region: Optional[str] = "esp-es") -> Dict[str, Union[str, int]]:
    """
    A tool that performs internet search using DuckDuckGo's API.
    
    Args:
        query (str): The search query.
        category (str, optional): The category for targeted searches. Defaults to None.
        region (str, optional): The region for localized search results. Defaults to "us-en".
        
    Returns:
        Dict[str, Union[str, int]]: The search results.
        
    Raises:
        ValueError: If query is not provided.
        Exception: If an error occurred during the API request.
    """
    if not query:
        raise ValueError("query is required")
    
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "ia": category, "kl": region}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error occurred during the API request: {e}")

schema = {
    "name": "internet_search_tool",
    "description": "A tool that performs internet search using DuckDuckGo's API.",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query."
            },
            "category": {
                "type": "string",
                "description": "The category for targeted searches."
            },
            "region": {
                "type": "string",
                "description": "The region for localized search results."
            }
        },
        "required": ["query"]
    }
}
