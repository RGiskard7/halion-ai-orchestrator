# 🧠 OpenAI Modular MCP Framework

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/)

Este proyecto implementa un entorno modular estilo MCP (Model-Context-Protocol), diseñado para crear asistentes inteligentes capaces de invocar herramientas externas ("tools") mediante *function calling* de OpenAI, con una interfaz en Streamlit.

> Plataforma extensible para construir, gestionar y desplegar asistentes IA con capacidades personalizadas.

---

## 🚀 Características Principales

✅ **Arquitectura Modular**: Carga dinámica y edición en caliente de herramientas Python  
✅ **Interfaz Dual**: Chat con IA + Panel de administración completo  
✅ **Sin Reinicios**: Añade, edita y gestiona herramientas sin detener el servidor  
✅ **Transparencia Total**: Logs detallados, exportables en CSV/JSON  
✅ **Gestión Integrada**: Variables de entorno editables desde la UI  
✅ **Control de Herramientas**: Activación/desactivación y post-procesado configurable  
✅ **Generación con IA**: Creación automática de herramientas mediante descripción en lenguaje natural  
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
- Visualización de herramientas activas

### ⚙️ Panel de Administración
- **Herramientas**: 
  - Cargar, recargar y crear tools dinámicas
  - Activar/desactivar herramientas individualmente
  - Control de post-procesado por herramienta
  - Generación automática con IA
- **Variables**: Gestión del archivo `.env` desde la UI
- **Logs**: Visualización y exportación de registros

---

## 🧰 Creación de Herramientas

### Método 1: Generación con IA
1. Navega a **Admin > Herramientas > 🤖 Generar con IA**
2. Describe la herramienta que necesitas en lenguaje natural
3. La IA generará automáticamente:
   - Nombre y descripción
   - Schema JSON de parámetros
   - Código Python de implementación
   - Configuración de post-procesado

### Método 2: Creación Manual
1. Navega a **Admin > Herramientas > ✏️ Crear Manualmente**
2. Define el nombre, descripción y comportamiento de post-procesado
3. Configura el schema JSON:

```json
{
  "type": "object",
  "properties": {
    "param1": {
      "type": "string",
      "description": "Descripción del parámetro"
    }
  },
  "required": ["param1"]
}
```

4. Implementa la función Python:

```python
def mi_herramienta(param1):
    '''
    Documentación de la herramienta
    '''
    return f"Resultado: {param1}"
```

### Método 3: Creando un archivo Python

Crea un archivo en la carpeta `tools/` con la siguiente estructura:

```python
def mi_nueva_herramienta(param1, param2="valor_default"):
    # Lógica de la herramienta
    return f"Resultado: {param1}, {param2}"

schema = {
  "name": "mi_nueva_herramienta",
  "description": "Descripción de lo que hace la herramienta",
  "postprocess": True,  # Controla si la IA procesa el resultado
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
   - Verifica si la herramienta está activa
   - Invoca la tool Python seleccionada con los argumentos extraídos
   - Registra la ejecución en los logs
   - Si la herramienta tiene post-procesado activado:
     - Envía el resultado a GPT para contextualización
   - Si no tiene post-procesado:
     - Devuelve el resultado directamente
5. El usuario recibe la respuesta procesada o directa según la configuración

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
- Control granular del post-procesado por herramienta
- Manejo de excepciones para evitar fallos en cascada
- (Próximamente) Control de acceso basado en usuarios y permisos

---

## 🧭 Roadmap

- **Base de datos**: Soporte a SQLite/PostgreSQL para persistencia
- **Autenticación**: Sistema de login y permisos diferenciados
- **CLI**: Herramienta de línea de comandos para gestión
- **Editor Visual**: Creación de tools sin escribir código
- **Toolchains**: Encadenamiento automático de herramientas
- **Multi-LLM**: Compatibilidad con otras APIs (Claude, Gemini, etc.)
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

- **Asistente Personalizado**: Crea un asistente IA con funciones específicas
- **Laboratorio de Experimentación**: Prueba nuevas ideas de herramientas
- **Prototipado Rápido**: Base para integraciones con web, apps móviles, bots
- **Automatización**: Conecta APIs externas a través de herramientas personalizadas
- **Educación**: Plataforma para aprender sobre LLMs y function calling
