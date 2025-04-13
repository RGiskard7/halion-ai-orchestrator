from typing import Dict, Optional, Union
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def obtener_info_libro(titulo: Optional[str] = None, isbn: Optional[str] = None, autor: Optional[str] = None, limit: Optional[int] = 5) -> Dict[str, Union[str, list]]:
    """
    Obtiene información de libros a partir de un título, ISBN o autor.
    
    Args:
        titulo (str, optional): Título del libro.
        isbn (str, optional): ISBN del libro.
        autor (str, optional): Nombre del autor.
        limit (int, optional): Número máximo de resultados a devolver. Defaults to 5.
    
    Returns:
        Dict[str, Union[str, list]]: Información de los libros encontrados.
        
    Raises:
        ValueError: Si no se proporciona ningún parámetro de búsqueda.
        Exception: Si ocurre un error al realizar la solicitud a la API.
    """
    # Validaciones
    if not titulo and not isbn and not autor:
        raise ValueError("Debe proporcionar al menos un título, ISBN o autor para buscar.")

    # Construir la consulta
    query = titulo if titulo else isbn if isbn else autor
    url = f"http://openlibrary.org/search.json?q={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error si la respuesta no es exitosa
        data = response.json()
        
        # Limitar resultados
        libros = data.get('docs', [])[:limit]
        
        return {"libros": libros}
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error en la solicitud a la API: {e}")

schema = {
    "name": "obtener_info_libro",
    "description": "Obtiene información de libros a partir de un título, ISBN o autor.",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "titulo": {
                "type": "string",
                "description": "Título del libro."
            },
            "isbn": {
                "type": "string",
                "description": "ISBN del libro."
            },
            "autor": {
                "type": "string",
                "description": "Nombre del autor."
            },
            "limit": {
                "type": "integer",
                "description": "Número máximo de resultados a devolver. Defaults to 5."
            }
        },
        "required": []
    }
}
