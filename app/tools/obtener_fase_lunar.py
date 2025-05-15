from typing import Dict, Union
import os
from dotenv import load_dotenv
from datetime import datetime
import math

# Cargar variables de entorno
load_dotenv()

def obtener_fase_lunar() -> Dict[str, Union[str, int]]:
    """
    Determina la fase lunar actual basada en la fecha actual.
    
    Returns:
        Dict[str, Union[str, int]]: Un diccionario que contiene la fase lunar actual y la fecha.
        
    Raises:
        ValueError: Si la fecha es inválida.
    """
    try:
        # Obtener la fecha actual
        fecha_actual = datetime.now()
        # Calcular el número de días desde la luna nueva (1 de enero de 2000)
        luna_nueva = datetime(2000, 1, 6)
        dias_desde_luna_nueva = (fecha_actual - luna_nueva).days
        
        # Calcular la fase lunar
        fase = dias_desde_luna_nueva % 29.53
        
        if fase < 1:
            fase_lunar = "Luna Nueva"
        elif fase < 14.77:
            fase_lunar = "Creciente"
        elif fase < 14.77 + 1:
            fase_lunar = "Luna Llena"
        else:
            fase_lunar = "Menguante"
        
        return {
            "fase_lunar": fase_lunar,
            "fecha": fecha_actual.strftime("%Y-%m-%d")
        }
    except Exception as e:
        raise Exception(f"Error en obtener_fase_lunar: {e}")

schema = {
    "name": "obtener_fase_lunar",
    "description": "Obtiene la fase lunar actual en base a la fecha actual.",
    "postprocess": False,  # No se necesita procesamiento adicional
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
