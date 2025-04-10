from typing import Dict, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
import json
import os

load_dotenv()

def get_hotel_info(hotel_name: str) -> Optional[Dict]:
    """
    Connects to a MongoDB database and retrieves information about a specific hotel.

    Args:
        hotel_name (str): The name of the hotel to search for.

    Returns:
        Optional[Dict]: A dictionary containing the hotel's information, or None if the hotel was not found.

    Raises:
        ValueError: If the connection string or database name or collection name is not found in environment variables.
        Exception: If any error occurs while connecting to the database or retrieving the data.
    """
    connection_string = os.getenv("MONGO_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("No connection string found. Please add MONGO_CONNECTION_STRING to your environment variables.")

    database_name = os.getenv("MONGO_DATABASE_NAME")
    if not database_name:
        raise ValueError("No database name found. Please add MONGO_DATABASE_NAME to your environment variables.")

    collection_name = os.getenv("MONGO_COLLECTION_NAME")
    if not collection_name:
        raise ValueError("No collection name found. Please add MONGO_COLLECTION_NAME to your environment variables.")    

    try:
        client = MongoClient(connection_string)
        database = client[database_name]
        collection = database[collection_name]

        hotel_info = collection.find_one({"name": hotel_name})

        if hotel_info is not None:
            # Convertir ObjectId y otros tipos BSON a str para serialización JSON
            hotel_info = json.loads(json.dumps(hotel_info, default=str))

        return hotel_info
    except Exception as e:
        raise Exception(f"An error occurred while retrieving the hotel information: {e}")

schema = {
    "name": "get_hotel_info",
    "description": "Retrieves information about a specific hotel from a MongoDB database.",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "hotel_name": {
                "type": "string",
                "description": "The name of the hotel to search for."
            }
        },
        "required": ["hotel_name"]
    }
}
