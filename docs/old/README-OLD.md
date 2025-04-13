# 🧠 OpenAI Modular MCP Framework

[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.44+-red.svg)](https://streamlit.io/)
[![OpenAI API](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/)
[![PyMongo](https://img.shields.io/badge/PyMongo-4.6.1-blueviolet.svg)](https://pymongo.readthedocs.io/)

<p align="center">
  <img src="https://via.placeholder.com/1200x300.png?text=OpenAI+Modular+MCP+Framework" alt="OpenAI Modular MCP Banner" width="100%" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/>
</p>

Este proyecto implementa un entorno modular estilo MCP (Model-Context-Protocol), diseñado para crear asistentes inteligentes capaces de invocar herramientas externas ("tools") mediante *function calling* de OpenAI, con una interfaz en Streamlit.

> Plataforma extensible para construir, gestionar y desplegar asistentes IA con capacidades personalizadas a través de herramientas modulares.

---

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación](#️-instalación)
- [Ejecución](#-ejecución)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Interfaz Visual](#️-interfaz-visual)
- [Creación de Herramientas](#-creación-de-herramientas)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Flujo de Ejecución](#-flujo-de-ejecución)
- [Sistema de Registro y Monitoreo](#-sistema-de-registro-y-monitoreo)
- [Integración con APIs Externas](#-integración-con-apis-externas)
- [Seguridad y Buenas Prácticas](#-seguridad-y-buenas-prácticas)
- [Roadmap](#-roadmap)
- [Contribuciones](#-contribuciones)
- [Solución de Problemas Comunes](#-solución-de-problemas-comunes)
- [Casos de Uso](#-casos-de-uso)
- [Créditos](#-créditos)

---

## 🚀 Características Principales

✅ **Arquitectura Modular**: Carga dinámica y edición en caliente de herramientas Python  
✅ **Interfaz Dual**: Chat con IA + Panel de administración completo  
✅ **Sin Reinicios**: Añade, edita y gestiona herramientas sin detener el servidor  
✅ **Transparencia Total**: Logs detallados, exportables en CSV/JSON  
✅ **Gestión Integrada**: Variables de entorno editables desde la UI  
✅ **Control de Herramientas**: Activación/desactivación y post-procesado configurable  
✅ **Generación con IA**: Creación automática de herramientas mediante descripción en lenguaje natural  
✅ **Compatibilidad con OpenAI**: Soporte para GPT-4, GPT-4-Turbo y GPT-3.5-Turbo  
✅ **Personalización**: Control avanzado de parámetros de generación (temperatura, top_p, etc.)  
✅ **Detección Automática**: Identificación de variables de entorno en código generado  
✅ **Integración con Bases de Datos**: Conectores para MongoDB y otros sistemas  
✅ **Sistema de Depuración**: Logs detallados para diagnóstico y solución de problemas  

---

## 📦 Requisitos del Sistema

- **Python**: 3.13 o superior  
- **API Key**: OpenAI (GPT-4 o GPT-3.5-Turbo)  
- **Dependencias Core**:
  - Streamlit 1.44+
  - OpenAI SDK 1.72+
  - PyMongo 4.6.1
  - Python-dotenv 1.1+
  - DuckDuckGo-Search 8.0+
- **Dependencias Opcionales** (según herramientas activadas):
  - Servicios meteorológicos: OpenWeatherMap API
  - Información de películas: OMDB/TMDB API
  - Noticias: News API
  - Almacenamiento: MongoDB (para herramientas que acceden a bases de datos)

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

Para una instalación con todas las dependencias opcionales:

```bash
pip install -r requirements-full.txt
```

---

## 🧪 Ejecución

```bash
# Método 1: Activar el entorno virtual y ejecutar directamente
source venv/bin/activate
streamlit run streamlit_app.py

# Método 2: Usar Python del entorno virtual directamente
source venv/bin/activate
python -m streamlit run streamlit_app.py

# La interfaz estará disponible en http://localhost:8501
```

> **Nota**: Es importante usar el Python del entorno virtual donde se instalaron las dependencias para evitar problemas de importación.

---

## 🏗️ Arquitectura del Sistema

La arquitectura de OpenAI Modular MCP está diseñada con un enfoque en modularidad, extensibilidad y mantenibilidad:

### Componentes Principales

1. **Núcleo de Ejecución (executor.py)**:
   - Gestiona la comunicación con la API de OpenAI
   - Implementa la lógica de detección de function calls
   - Orquesta la ejecución de herramientas y post-procesamiento

2. **Gestor de Herramientas (tool_manager.py)**:
   - Carga dinámicamente herramientas desde la carpeta `tools/`
   - Mantiene registro de herramientas activas/inactivas
   - Gestiona los errores de carga

3. **Registro Dinámico (dynamic_tool_registry.py)**:
   - Permite crear y registrar herramientas en tiempo de ejecución
   - Facilita la persistencia de herramientas generadas

4. **Gestor de Entorno (env_manager.py)**:
   - Administra variables de entorno y credenciales
   - Proporciona APIs para actualización en tiempo real

5. **Sistema de Logging (logger.py)**:
   - Registra todas las invocaciones de herramientas
   - Facilita la exportación y análisis de logs

6. **Interfaz de Usuario (streamlit_app.py)**:
   - Proporciona la experiencia de chat con IA
   - Implementa el panel de administración completo

---

## 🖥️ Interfaz Visual

La plataforma ofrece dos interfaces principales integradas en una aplicación Streamlit:

### 💬 Chat IA
- **Interfaz Conversacional**: Diseño limpio y responsive
- **Configuración Avanzada**: 
  - Selección de modelo (GPT-4, GPT-4-Turbo, GPT-3.5-Turbo)
  - Control de temperatura y otros parámetros
  - Configuración de tokens máximos
  - Personalización de penalties y top_p
  - Opción de semilla para reproducibilidad
- **Historial de Conversación**: Persistencia durante la sesión
- **Dashboard de Herramientas**: Vista rápida de herramientas activas

### ⚙️ Panel de Administración
- **Gestión de Herramientas**: 
  - Vista tabulada con opciones de paginación
  - Activación/desactivación con un clic
  - Edición de código integrada
  - Visualización detallada
  - Creación y eliminación de herramientas
  - Diagnóstico de errores

- **Variables de Entorno**:
  - Editor visual del archivo `.env`
  - Almacenamiento seguro de credenciales
  - Detección automática de variables en herramientas
  - Recarga en tiempo real

- **Sistema de Logs**:
  - Visualización cronológica de invocaciones
  - Exportación en formatos CSV y JSON
  - Detalles de ejecución y resultados

---

## 🧰 Creación de Herramientas

El sistema ofrece múltiples métodos para crear nuevas herramientas:

### Método 1: Generación con IA (Recomendado)
1. Navega a **Admin > Herramientas > 🤖 Generar con IA**
2. Describe la herramienta que necesitas en lenguaje natural
3. La IA generará automáticamente:
   - Nombre semántico y descripción detallada
   - Schema JSON de parámetros completo
   - Código Python optimizado
   - Configuración de post-procesado apropiada
   - Detección automática de variables de entorno necesarias

### Método 2: Creación Manual vía UI
1. Navega a **Admin > Herramientas > ✏️ Crear Manualmente**
2. Define el nombre, descripción y comportamiento de post-procesado
3. Configura el schema JSON con los parámetros necesarios
4. Implementa la función Python en el editor integrado

### Método 3: Creación de Archivos Python
1. Crea un nuevo archivo en la carpeta `tools/` con el formato:
```python
def nombre_herramienta(param1, param2="valor_default"):
    """
    Documentación detallada de la herramienta.
    
    Args:
        param1: Descripción del primer parámetro
        param2: Descripción del segundo parámetro (opcional)
        
    Returns:
        Descripción del valor retornado
    """
    # Implementación de la herramienta
    return resultado

schema = {
  "name": "nombre_herramienta",
  "description": "Descripción detallada para que la IA entienda cuándo usar esta herramienta",
  "postprocess": True,  # True si la IA debe procesar el resultado, False para salida directa
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {"type": "string", "description": "Descripción completa del parámetro"},
      "param2": {"type": "string", "description": "Descripción del parámetro opcional"}
    },
    "required": ["param1"]
  }
}
```

### Buenas Prácticas para Herramientas
- Utiliza nombres descriptivos en snake_case
- Proporciona docstrings detallados
- Maneja excepciones apropiadamente
- Usa variables de entorno para credenciales
- Implementa validación de parámetros
- Define claramente los tipos de retorno

---

## 📂 Estructura del Proyecto

```
.
├── tools/                       # Herramientas disponibles
│   ├── buscar_en_internet.py    # Búsqueda web vía DuckDuckGo
│   ├── get_current_weather.py   # Clima con OpenWeatherMap
│   ├── get_hotel_info.py        # Información de hoteles (MongoDB)
│   ├── fetch_movie_info.py      # Datos de películas (OMDB/TMDB)
│   ├── get_latest_news.py       # Noticias actuales
│   ├── saludar.py               # Ejemplo simple
│   └── ...                      # Otras herramientas
├── debug_logs/                  # Logs de diagnóstico
│   └── file_creation_debug.log  # Registro de creación de archivos
├── streamlit_app.py             # Aplicación principal Streamlit
├── executor.py                  # Orquestador central
├── tool_manager.py              # Gestión de herramientas
├── dynamic_tool_registry.py     # Registro dinámico de herramientas
├── logger.py                    # Sistema de logs
├── env_manager.py               # Gestión de variables de entorno
├── tool_calls.log               # Registro de invocaciones
├── .env                         # Variables de entorno (privado)
├── .env.example                 # Plantilla de variables de entorno
├── .tool_status.json            # Estado de activación de herramientas
├── requirements.txt             # Dependencias básicas
├── pyproject.toml               # Configuración del proyecto
├── roadmap.md                   # Plan de desarrollo futuro
├── main_context.md              # Documentación de arquitectura 
└── README.md                    # Este archivo
```

---

## 🧠 Flujo de Ejecución

El flujo de ejecución en el sistema sigue estos pasos:

1. **Entrada del Usuario**: El usuario introduce un mensaje o consulta
2. **Preparación del Contexto**: Se recogen las herramientas activas y se preparan los schemas
3. **Consulta a OpenAI**: Se envía el mensaje con la lista de herramientas disponibles
4. **Detección de Intención**: El modelo de OpenAI decide si necesita invocar una herramienta
5. **Ejecución Condicional**:
   - Si no se requiere herramienta: Se devuelve la respuesta directa del modelo
   - Si se requiere herramienta:
     a. Se verifica que esté activa
     b. Se extraen los argumentos del JSON proporcionado
     c. Se ejecuta la función correspondiente
     d. Se registra la llamada en los logs
6. **Post-procesamiento**: 
   - Si la herramienta tiene post-procesado activado:
     a. El resultado se envía de vuelta a OpenAI
     b. El modelo genera una respuesta contextualizada
   - Si no tiene post-procesado:
     a. El resultado se devuelve directamente al usuario
7. **Presentación**: Se muestra el resultado al usuario en la interfaz

**Ejemplo completo**:
```
Usuario: "¿Cómo está el clima en Barcelona?"
→ OpenAI detecta intención de consultar clima
→ Invoca get_current_weather(location="Barcelona")
→ Se obtienen datos de OpenWeatherMap API
→ Se realiza post-procesado para generar respuesta natural
→ Usuario recibe: "En Barcelona hay 22°C con cielo despejado. La humedad es del 65% y hay viento ligero de 10 km/h."
```

---

## 📊 Sistema de Registro y Monitoreo

El framework implementa un sistema robusto de registro para auditoria y debugging:

### Logs de Invocación
- Cada llamada a herramienta se registra en `tool_calls.log`
- Formato JSON con:
  - Timestamp ISO 8601
  - ID de usuario
  - Nombre de función invocada
  - Argumentos completos
  - Resultado obtenido
  - Tiempo de ejecución

### Logs de Debug
- Registros detallados en `debug_logs/file_creation_debug.log`
- Tracking de:
  - Carga de herramientas
  - Creación de archivos
  - Errores detallados con tracebacks
  - Estado de entorno

### Interfaz de Visualización
- Panel dedicado en la UI para explorar logs
- Filtrado y ordenación
- Exportación en múltiples formatos
- Limpieza de registros

---

## 🔌 Integración con APIs Externas

El sistema permite integrar fácilmente servicios externos mediante herramientas dedicadas:

### APIs Soportadas
- **Búsqueda Web**: DuckDuckGo Search API
- **Clima**: OpenWeatherMap API
- **Películas**: OMDB API y TMDB API
- **Noticias**: News API
- **Bases de Datos**: MongoDB (para almacenamiento)

### Configuración de Credenciales
Las credenciales se gestionan mediante variables de entorno en el archivo `.env`:

```
OPENAI_API_KEY=sk-...
OPENWEATHERMAP_API_KEY=...
NEWS_API_KEY=...
OMDB_API_KEY=...
TMDB_API_KEY=...
MONGO_CONNECTION_STRING=...
```

Estas se pueden gestionar directamente desde la interfaz en **Admin > Variables de Entorno**.

---

## 🔐 Seguridad y Buenas Prácticas

El proyecto implementa diversas medidas de seguridad:

### Gestión de Credenciales
- Almacenamiento en `.env` (no en código)
- Visualización cifrada en la interfaz
- Carga dinámica en tiempo de ejecución

### Validación y Sanitización
- Validación de parámetros mediante JSON Schema
- Manejo defensivo de errores
- Sanitización de entradas

### Control de Acceso
- Activación/desactivación explícita de herramientas
- Control granular del post-procesado
- Logs de auditoría

### Buenas Prácticas
- Manejo estructurado de excepciones
- Timeouts para llamadas a APIs externas
- Retrocompatibilidad con versiones anteriores

---

## 🧭 Roadmap

Próximos desarrollos planificados:

### Corto Plazo (1-3 meses)
- **Persistencia Mejorada**: Integración con SQLite/PostgreSQL
- **Autenticación**: Sistema de login y permisos de usuarios
- **CLI**: Herramienta de línea de comandos para gestión

### Medio Plazo (3-6 meses)
- **Editor Visual**: Creación de herramientas sin código
- **Toolchains**: Encadenamiento automático de herramientas
- **Multi-LLM**: Soporte para Claude, Gemini y otros modelos
- **Tests Automatizados**: Cobertura completa con pytest

### Largo Plazo (6-12 meses)
- **Marketplace**: Repositorio compartido de herramientas
- **Deployment**: Containerización con Docker/Kubernetes
- **API REST**: Endpoints para integración con otros sistemas
- **Agentes Autónomos**: Herramientas auto-evolutivas

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas y apreciadas. Para participar:

1. Abre un issue para discutir el cambio propuesto
2. Haz fork del repositorio
3. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
4. Realiza tus cambios y haz commit (`git commit -m 'Add amazing feature'`)
5. Push a la rama (`git push origin feature/amazing-feature`)
6. Abre un Pull Request

### Guías de Contribución
- Sigue el estilo de código existente
- Escribe tests para nuevas funcionalidades
- Documenta cambios significativos
- Actualiza README y documentación relevante

---

## 🛠️ Solución de Problemas Comunes

### Problemas de Importación
Si encuentras errores como `ModuleNotFoundError`, asegúrate de:
- Ejecutar la aplicación dentro del entorno virtual donde instalaste las dependencias
- Instalar todas las dependencias con `pip install -r requirements.txt`
- Usar `python -m streamlit run streamlit_app.py` para ejecutar

### Conflictos con PyMongo y BSON
Para resolver problemas con MongoDB y BSON:
- Usa PyMongo 4.6.1 o superior: `pip install pymongo==4.6.1`
- Evita instalar el paquete `bson` independiente
- Para serializar ObjectId y otros tipos BSON, usa `json.dumps(obj, default=str)`

### Error de API Key
Si encuentras errores de autenticación con OpenAI:
- Verifica tu API key en el archivo `.env`
- Asegúrate de que la API key tiene permisos y saldo suficiente
- Recarga las variables de entorno desde Admin > Variables de Entorno

---

## 🧭 Casos de Uso

### Asistente Corporativo Personalizado
Configura un asistente con herramientas específicas para:
- Consultar bases de datos internas
- Acceder a documentación técnica
- Interactuar con sistemas empresariales

### Plataforma Educativa Interactiva
Desarrolla un asistente para entornos educativos que pueda:
- Buscar recursos académicos
- Explicar conceptos complejos
- Generar ejercicios personalizados

### Automatización de Operaciones
Crea un sistema para automatizar tareas repetitivas:
- Monitoreo de sistemas
- Alertas basadas en datos
- Informes automatizados

### Integración Multiservicio
Unifica múltiples APIs en una interfaz conversacional:
- Agregación de noticias
- Datos meteorológicos
- Información de productos

### Plataforma de Experimentación
Utiliza el framework como base para:
- Prototipar nuevas ideas
- Testear la efectividad de diferentes prompts
- Evaluar modelos y enfoques

---

## 📚 Créditos

Desarrollado por **RGiskard7** ✨ con ❤️ por el poder de lo modular, lo limpio y lo hackeable.

### Agradecimientos Especiales
- Comunidad OpenAI por la documentación y APIs
- Equipo de Streamlit por el framework de interfaz
- Todos los contribuidores de código abierto cuyas bibliotecas hacen posible este proyecto
