def resumir_texto(texto):
    """
    Devuelve un resumen simple del texto original.
    """
    oraciones = texto.split('.')
    resumen = '. '.join(oraciones[:2]) + '.' if len(oraciones) > 2 else texto
    return {"resumen": resumen}

schema = {
  "name": "resumir_texto",
  "description": "Devuelve un resumen simple del texto original",
  "parameters": {
    "type": "object",
    "properties": {
      "texto": {
        "type": "string",
        "description": "Texto a resumir"
      }
    },
    "required": [
      "texto"
    ]
  },
  "postprocess": False
}
