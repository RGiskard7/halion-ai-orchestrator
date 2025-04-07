from duckduckgo_search import ddg

def buscar_en_internet(query: str, max_results: int = 5) -> str:
    try:
        resultados = ddg(query, max_results=max_results)
        if not resultados:
            return "No se han encontrado resultados relevantes."

        resumen = f"📌 **Resumen de resultados para**: _{query}_\n\n"
        fuentes = []
        for i, r in enumerate(resultados):
            titulo = r.get("title", "Sin título")
            snippet = r.get("body", "Sin descripción")
            enlace = r.get("href", "#")

            resumen += f"**{i+1}. {titulo}**\n"
            resumen += f"{snippet}\n\n"
            fuentes.append(f"[{i+1}]({enlace})")

        resumen += "---\n"
        resumen += "🔗 **Fuentes**: " + " · ".join(fuentes)
        return resumen

    except Exception as e:
        return f"❌ Ocurrió un error al realizar la búsqueda: {str(e)}"

schema = {
  "name": "buscar_en_internet",
  "description": "Permite buscar en internet (DuckDuckGo) cualquier cosa indicada",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Término o pregunta a buscar en internet"
      },
      "max_results": {
        "type": "integer",
        "description": "Número máximo de resultados",
        "default": 5
      }
    },
    "required": [
      "query"
    ]
  }
}
