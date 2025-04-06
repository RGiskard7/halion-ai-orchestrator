import json
import requests
import os

def get_current_weather(location: str, unit: str = "metric") -> str:
    """
    Obtiene el clima actual en una ubicación específica utilizando la API de OpenWeatherMap.

    Args:
        location (str): Nombre de la ciudad o ubicación (e.g., "Madrid").
        unit (str): Unidad de medida para la temperatura. Puede ser "metric" (Celsius) o "imperial" (Fahrenheit).

    Returns:
        str: Información del clima actual en formato JSON.
    """
    # Configuración de la API
    api_key = "dc782a7368ea781210ccdc4aed4c880a"
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    # Parámetros de la solicitud
    params = {
        "q": location,  # Nombre de la ubicación
        "appid": api_key,
        "units": unit  # "metric" para Celsius, "imperial" para Fahrenheit
    }

    try:
        # Realizar la solicitud GET
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP

        # Procesar la respuesta
        data = response.json()
        return json.dumps({
            "location": data.get("name", location),
            "temperature": data["main"]["temp"],
            "unit": "Celsius" if unit == "metric" else "Fahrenheit",
            "humidity": data["main"]["humidity"],  # Humedad en porcentaje
            "pressure": data["main"]["pressure"],  # Presión atmosférica en hPa
            "wind_speed": data["wind"]["speed"],  # Velocidad del viento en m/s o mph
            "wind_direction": data["wind"].get("deg", "N/A"),  # Dirección del viento en grados
            "description": data["weather"][0]["description"],  # Descripción del clima
        }, indent=2)

    except requests.exceptions.HTTPError as http_err:
        return json.dumps({"error": f"HTTP error: {http_err}"})
    except Exception as err:
        return json.dumps({"error": f"Unexpected error: {err}"})

schema = {
  "name": "get_current_weather",
  "description": "Obtén el clima actual en una ubicación especificada.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "Ciudad y estado, e.g., Madrid, ES."
      },
      "unit": {
        "type": "string",
        "enum": [
          "metric",
          "imperial"
        ],
        "description": "Unidades (metric para Celsius, imperial para Fahrenheit)."
      }
    },
    "required": [
      "location"
    ]
  }
}
