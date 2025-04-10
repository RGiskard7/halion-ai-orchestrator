from typing import Dict, Optional
import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from rapidfuzz import process

load_dotenv()

def navigate_app_screen(screen_name: str, params: Optional[Dict[str, str]] = None) -> str:
    """
    Devuelve la ruta URL completa para la pantalla solicitada en la app.
    
    Args:
        screen_name (str): Nombre de la pantalla a la que se desea navegar.
        params (dict, optional): Parámetros adicionales necesarios (ej. hotelName).
    
    Returns:
        str: URL completa de la pantalla.
    """
    base_url = os.getenv("APP_BASE_URL", "https://www.mihotel.com")
    hotel_id = ""
    reservation_id = params.get("reservationId") if params else ""

    # Si se solicita un hotel, buscar el id correspondiente
    if params and "hotelName" in params:
        hotel_name = params["hotelName"]
        try:
            # Conectar con MongoDB
            mongo_client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
            db = mongo_client[os.getenv("MONGO_DATABASE_NAME")]
            collection = db[os.getenv("MONGO_COLLECTION_NAME")]
            hotel_docs = list(collection.find({}, {"_id": 0, "id": 1, "name": 1}))

            # Extraer nombres e IDs
            name_list = [doc["name"] for doc in hotel_docs]
            match, score, index = process.extractOne(hotel_name, name_list)

            if score > 80:
                hotel_id = hotel_docs[index]["id"]
            else:
                return f"No se encontró ningún hotel que coincida con '{hotel_name}'."

        except Exception as e:
            return f"Error al buscar el hotel: {str(e)}"

    # Mapear rutas
    screens = {
        "home": "/home",
        "ai": "/ai",
        "profile": "/profile",
        "hotel_details": f"/hotel/{hotel_id}",
        "hotel_reservation": f"/hotel/reservation/{hotel_id}",
        "reservation_confirmation": f"/hotel/reservation/confirmation/{reservation_id}"
    }

    if screen_name not in screens:
        return f"Pantalla '{screen_name}' no reconocida. Las disponibles son: {', '.join(screens.keys())}"

    return f"{base_url}{screens[screen_name]}"

schema = {
    "name": "navigate_app_screen",
    "description": "Navega a una pantalla específica de una aplicación de hoteles y devuelve la ruta URL correspondiente.",
    "postprocess": False,
    "parameters": {
        "type": "object",
        "properties": {
            "screen_name": {
                "type": "string",
                "description": "Nombre de la pantalla a la que se desea navegar. Ejemplos: home, profile, hotel_details, hotel_reservation, reservation_confirmation."
            },
            "params": {
                "type": "object",
                "description": "Parámetros adicionales requeridos para esa pantalla (como hotelName o reservationId).",
                "properties": {
                    "hotelName": { "type": "string" },
                    "reservationId": { "type": "string" }
                }
            }
        },
        "required": ["screen_name"]
    }
}