# 🧠 OpenAI Modular MCP Framework

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/)

Este proyecto implementa un entorno modular estilo MCP (Model-Context-Protocol), diseñado para crear asistentes inteligentes capaces de invocar herramientas externas ("tools") mediante *function calling* de OpenAI, con una interfaz profesional en Streamlit.

> Plataforma extensible para construir, gestionar y desplegar asistentes IA con capacidades personalizadas.

---

## 🚀 Características Principales

✅ **Arquitectura Modular**: Carga dinámica y edición en caliente de herramientas Python  
✅ **Interfaz Dual**: Chat con IA + Panel de administración completo  
✅ **Sin Reinicios**: Añade, edita y gestiona herramientas sin detener el servidor  
✅ **Transparencia Total**: Logs detallados, exportables en CSV/JSON  
✅ **Gestión Integrada**: Variables de entorno editables desde la UI  
✅ **Compatibilidad con OpenAI**: Soporte para GPT-4 y GPT-3.5-Turbo  
✅ **Personalización**: Control de temperatura y selección de modelo  

---

## 📦 Requisitos del Sistema

- **Python**: 3.9 o superior  
- **API Key**: OpenAI (GPT-4 o GPT-3.5-Turbo)  
- **Dependencias**: Streamlit, OpenAI, DuckDuckGo-Search (ver `requirements.txt`)  
- **(Opcional)**: Claves API para servicios externos (OpenWeather, etc.)

---

## 🛠️ Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/openai_modular_mcp.git
cd openai_modular_mcp

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env  # Editar para añadir tu API key de OpenAI
```

---

## 🧪 Ejecución

```bash
# Iniciar la aplicación Streamlit
streamlit run streamlit_app.py

# La interfaz estará disponible en http://localhost:8501
```

---

## 🖥️ Interfaz Visual

### 💬 Chat IA
- Soporte para texto
- Selección de modelo y temperatura
- Historial de conversación persistente

### ⚙️ Panel de Administración
- **Herramientas**: Cargar, recargar y crear tools dinámicas
- **Variables**: Gestión del archivo `.env` desde la UI
- **Logs**: Visualización y exportación de registros

---

## 🧰 Creación de Herramientas

### Método 1: Desde la UI (Sin código adicional)

1. Navega a la pestaña **Admin > Herramientas**
2. Define el esquema JSON de parámetros:

```json
{
  "type": "object",
  "properties": {
    "ciudad": {"type": "string", "description": "Ciudad a consultar"}
  },
  "required": ["ciudad"]
}
```

3. Implementa la función Python:

```python
def obtener_hora(ciudad):
    from datetime import datetime
    return f"En {ciudad} son las {datetime.now().strftime('%H:%M:%S')}"
```

### Método 2: Creando un archivo Python

Crea un archivo en la carpeta `tools/` con la siguiente estructura:

```python
def mi_nueva_herramienta(param1, param2="valor_default"):
    # Lógica de la herramienta
    return f"Resultado: {param1}, {param2}"

schema = {
  "name": "mi_nueva_herramienta",
  "description": "Descripción de lo que hace la herramienta",
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {"type": "string", "description": "Descripción del parámetro"},
      "param2": {"type": "string", "description": "Parámetro opcional"}
    },
    "required": ["param1"]
  }
}
```

---

## 📂 Estructura del Proyecto

```
.
├── tools/                 # Carpeta con herramientas (.py)
│   ├── buscar_en_internet.py  # Búsqueda web vía DuckDuckGo
│   ├── get_current_weather.py # Clima con OpenWeatherMap
│   ├── saludar.py            # Ejemplo simple
│   └── send_email.py         # Envío de correos
├── streamlit_app.py       # Interfaz principal Streamlit
├── executor.py            # Orquestador de llamadas a GPT
├── tool_manager.py        # Gestión de tools desde disco
├── dynamic_tool_registry.py # Tools creadas desde la UI
├── logger.py              # Logging de invocaciones
├── env_manager.py         # Gestión del archivo .env
├── .env.example           # Plantilla para variables de entorno
├── .tool_status.json      # Control de tools activas
├── requirements.txt       # Dependencias del proyecto
└── main_context.md        # Documentación de arquitectura
```

---

## 🧠 Flujo de Ejecución

1. El usuario escribe un mensaje en el chat
2. El mensaje se envía a la API de OpenAI con la lista de tools disponibles
3. El modelo decide si usar `function_call` basado en la intención del usuario
4. Si corresponde, el sistema:
   - Invoca la tool Python seleccionada con los argumentos extraídos
   - Registra la ejecución en los logs
   - Devuelve el resultado como parte de la respuesta
5. El usuario recibe una respuesta contextualizada que incorpora el resultado

**Ejemplo**: _"¿Qué tiempo hace en Madrid?"_ → usa `get_current_weather` → muestra datos meteorológicos

---

## 📝 Sistema de Registro

Cada llamada a una herramienta se guarda en `tool_calls.log` con:
- Timestamp de ejecución
- ID de usuario (para futuras implementaciones multi-usuario)
- Nombre de la función invocada
- Argumentos proporcionados
- Resultado obtenido
- Tiempo de ejecución

Los logs pueden exportarse desde la interfaz en formato CSV o JSON para análisis posterior.

---

## 🔐 Seguridad y Buenas Prácticas

- Las API Keys se almacenan en `.env` (nunca en el código)
- Las herramientas deben estar explícitamente activadas para ser utilizadas
- Validación de parámetros antes de la ejecución
- Manejo de excepciones para evitar fallos en cascada
- (Próximamente) Control de acceso basado en usuarios y permisos

---

## 🧭 Roadmap

- **Base de datos**: Soporte a SQLite/PostgreSQL para persistencia de usuarios y logs
- **Autenticación**: Sistema de login y permisos diferenciados
- **CLI**: Herramienta de línea de comandos para registrar/editar tools
- **Editor Visual**: Creación de tools sin escribir código (drag & drop)
- **Toolchains**: Encadenamiento automático de herramientas para tareas complejas
- **Multi-LLM**: Compatibilidad con otras APIs (Claude, Gemini, LLaMA, etc.)
- **Despliegue**: Guías para Docker, Kubernetes y servicios cloud

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Abre un issue para discutir el cambio propuesto
2. Haz fork del repositorio
3. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
4. Realiza tus cambios y haz commit (`git commit -m 'Add amazing feature'`)
5. Push a la rama (`git push origin feature/amazing-feature`)
6. Abre un Pull Request

---

## 📚 Créditos

Desarrollado por **RGiskard7** ✨ con ❤️ por el poder de lo modular, lo limpio y lo hackeable.

---

## 🧭 Casos de Uso

- **Asistente Personalizado**: Crea un asistente IA con funciones específicas para tu negocio
- **Laboratorio de Experimentación**: Prueba nuevas ideas de herramientas en tiempo real
- **Prototipado Rápido**: Base para integraciones con web, apps móviles, bots, etc.
- **Automatización**: Conecta APIs externas a través de herramientas personalizadas
- **Educación**: Plataforma para aprender sobre LLMs y function calling
