# 🧩 HALion: Modular Intelligence Orchestrator - Documentación Técnica

## 📄 Visión General

OpenAI Modular MCP (Model-Context-Protocol) es una plataforma extensible para la creación, gestión y despliegue de asistentes IA con capacidades personalizadas a través de herramientas modulares. El sistema implementa un enfoque arquitectónico que permite a los modelos de lenguaje de OpenAI interactuar con funciones externas de forma estructurada y administrada.

> Este documento proporciona una visión técnica completa del proyecto, su arquitectura, componentes y flujos de trabajo, sirviendo como referencia técnica principal para desarrolladores.

## 🎯 Objetivos del Proyecto

- **Extensibilidad**: Proporcionar una base robusta para construir asistentes IA personalizados
- **Modularidad**: Permitir la adición, modificación y eliminación de capacidades sin afectar al sistema central
- **Usabilidad**: Ofrecer una interfaz intuitiva tanto para usuarios finales como para administradores
- **Transparencia**: Registrar todas las interacciones y ejecuciones para análisis y auditoría
- **Seguridad**: Implementar buenas prácticas para el manejo de credenciales y ejecución de código
- **Control**: Proporcionar gestión granular de herramientas y su comportamiento
- **Diagnóstico**: Facilitar la detección y solución de problemas mediante logs detallados

## 🏗️ Arquitectura del Sistema

### Diagrama de Flujo Principal

```
Usuario → Interfaz Streamlit → Executor (chat_with_tools) → OpenAI API
Usuario → Interfaz Streamlit → Chat Service (chat_with_tools) → OpenAI API
                                       ↓
                                  ¿function_call?
                                       ↓
                                     Si → Tool Manager → ¿Tool Activa? → Herramienta
                                       ↓                      ↓
                                    Logger ← ← ← ← ← ← ← Resultado
                                       ↓
                              ¿Post-procesado?
                                       ↓
                                Si → OpenAI → Respuesta
                                No → Resultado Directo
                                       ↓
                                   Usuario
```

### Componentes Principales

#### 1. `app/main.py`

Interfaz de usuario construida con Streamlit que proporciona:

- **Chat con IA**: 
  - Interfaz conversacional con soporte para texto
  - Selección de modelo (GPT-4, GPT-4-Turbo, GPT-3.5-Turbo)
  - Control avanzado de parámetros (temperatura, max_tokens, top_p, penalties)
  - Opción de seed para reproducibilidad
  - Historial de conversación persistente
  - Visualización de herramientas activas

- **Panel de Administración**:
  - Gestión de herramientas (carga, recarga, creación, edición, eliminación)
  - Activación/desactivación individual de herramientas
  - Paginación para visualizar grandes conjuntos de herramientas
  - Control de post-procesado por herramienta
  - Generación automática de herramientas con IA
  - Detección automática de variables de entorno en código generado
  - Prompts especializados para function calling
  - Visualización y exportación de logs
  - Administración de variables de entorno con UI dedicada

#### 2. `app/core/executor.py`

Orquestador central que:

- Construye los mensajes para la API de OpenAI
- Incluye las definiciones de herramientas disponibles
- Procesa la respuesta y detecta llamadas a funciones
- Ejecuta las herramientas solicitadas
- Gestiona el post-procesado condicional de resultados
- Reincorpora los resultados según configuración
- Pasa parámetros avanzados (seed, penalties, etc.) a la API
- Gestiona el estado de la conversación y la lógica de interacción con el LLM.

#### 3. `app/services/chat_service.py`

Orquestador central que:

- Construye los mensajes para la API de OpenAI
- Incluye las definiciones de herramientas disponibles
- Procesa la respuesta y detecta llamadas a funciones
- Ejecuta las herramientas solicitadas
- Gestiona el post-procesado condicional de resultados
- Reincorpora los resultados según configuración
- Pasa parámetros avanzados (seed, penalties, etc.) a la API

#### 4. `app/core/tool_manager.py`

Gestor de herramientas que:

- Carga dinámicamente todas las herramientas desde el directorio `app/tools/`
- Mantiene un registro de herramientas activas/inactivas
- Gestiona el estado de post-procesado de cada herramienta
- Registra errores de carga para diagnóstico
- Proporciona acceso unificado a herramientas estáticas y dinámicas
- Genera logs detallados de depuración durante la carga

#### 5. `app/core/tool_definition_registry.py`

Registro de herramientas dinámicas que:

- Permite definir herramientas en tiempo de ejecución
- Soporta generación automática mediante IA
- Compila código Python desde la interfaz de usuario
- Persiste herramientas creadas dinámicamente a disco
- Gestiona el ciclo de vida de herramientas en memoria
- Valida el código generado antes de registrarlo
- Maneja errores de importación y compilación

#### 6. `app/core/logger.py`

Sistema de registro que:

- Documenta cada ejecución de herramienta
- Almacena metadatos, argumentos y resultados
- Proporciona funciones para exportar logs en JSON y CSV
- Facilita el análisis y depuración
- Mantiene un historial limitado para optimizar memoria

#### 7. `app/utils/env_manager.py`

Gestor de variables de entorno que:

- Lee y escribe en el archivo `.env`
- Permite añadir, modificar y eliminar variables
- Protege información sensible como API keys
- Proporciona mecanismos para recargar variables en tiempo de ejecución
- Asegura disponibilidad de variables en el entorno activo

## 🔄 Flujos de Trabajo

### 1. Flujo de Conversación

1. El usuario envía un mensaje a través de la interfaz de chat
2. `app/views/chat_view.py` llama a `chat_with_tools()` en `app/core/executor.py`
2. `app/views/chat_view.py` llama a `chat_with_tools()` en `app/services/chat_service.py`
3. `executor.py` prepara el contexto y envía la solicitud a OpenAI
3. `chat_service.py` prepara el contexto y envía la solicitud a OpenAI
4. OpenAI determina si se necesita invocar una herramienta
5. Si es necesario:
   - Se verifica si la herramienta está activa
   - `executor.py` obtiene la herramienta de `app/core/tool_manager.py`
   - `chat_service.py` obtiene la herramienta de `app/core/tool_manager.py`
   - Se ejecuta la herramienta y se registra en `app/core/logger.py`
   - Si tiene post-procesado activado:
     - El resultado se envía a GPT para contextualización
   - Si no tiene post-procesado:
     - El resultado se devuelve directamente
6. El usuario recibe la respuesta según la configuración

### 2. Flujo de Gestión de Herramientas

#### Carga Inicial:

1. Al iniciar la aplicación, `app/core/tool_manager.py` escanea el directorio `app/tools/`
2. Cada archivo Python se importa y se registra su función principal y schema
3. Se cargan las herramientas dinámicas previamente guardadas
4. Se aplica el estado de activación según `app/config/.tool_status.json`
5. Se generan logs detallados de errores o problemas durante la carga

#### Creación con IA:

1. El usuario describe la herramienta en lenguaje natural
2. La IA genera:
   - Nombre y descripción
   - Schema JSON de parámetros
   - Código Python de implementación
   - Configuración de post-procesado
3. Se detectan automáticamente las variables de entorno necesarias
4. El usuario revisa, configura las variables y puede modificar la generación
5. La herramienta se registra y persiste en disco

#### Creación Manual:

1. El usuario define:
   - Nombre y descripción
   - Comportamiento de post-procesado
   - Schema JSON de parámetros
   - Código Python
2. La herramienta se valida y registra
3. Opcionalmente se persiste a disco
4. Se marcan como activas automáticamente

## 📂 Estructura de Directorios

```
.
├── app/                         # Estructura modular de la aplicación
│   ├── components/              # Componentes reutilizables
│   ├── controllers/             # Lógica de controladores
│   ├── views/                   # Vistas de la interfaz
│   │   ├── admin_view.py        # Panel de administración
│   │   ├── chat_view.py         # Interfaz de chat
│   │   └── tools_view.py        # Gestión de herramientas 
│   ├── models/                  # Modelos de datos
│   ├── utils/                   # Utilidades
│   │   └── ai_generation.py     # Generación de herramientas/toolchains con IA
│   ├── core/                    # Funcionalidades centrales
│   │   ├── tool_definition_registry.py  # Registro y gestión de archivos de tools
│   │   ├── executor.py          # Orquestador de OpenAI
│   │   ├── logger.py            # Sistema de logs
│   │   └── tool_manager.py      # Gestión de herramientas
│   ├── services/                # Lógica de servicios (ej. chat)
│   │   └── chat_service.py      # Servicio principal de chat
│   ├── tools/                   # Herramientas disponibles
│   ├── config/                  # Archivos de configuración
│   │   └── .tool_status.json    # Estado de activación de herramientas
│   └── debug_logs/              # Logs específicos de la app
│       ├── file_creation_debug.log  # Registro detallado de errores
│       └── tool_calls.log       # Registro de invocaciones a herramientas
├── docs/                        # Documentación
│   ├── assets/                  # Recursos visuales (imágenes, iconos)
│   └── images/                  # Imágenes para documentación
├── .env                         # Variables de entorno (privado)
├── .env.example                 # Plantilla de variables
├── requirements.txt             # Dependencias
├── pyproject.toml               # Configuración del proyecto
├── run.py                       # Script de ejecución simplificado
├── main_context.md              # Arquitectura y contexto técnico
└── roadmap.md                   # Plan de desarrollo
```

## 🔌 Integración de Herramientas

### Anatomía de una Herramienta

Cada herramienta consta de dos componentes principales:

1. **Función Python**: Implementa la lógica de la herramienta
2. **Schema JSON**: Define la interfaz, parámetros y comportamiento

```python
# Ejemplo: tools/saludar.py

def saludar(nombre, formal=False):
    """
    Genera un saludo personalizado según el nombre y formalidad.
    
    Args:
        nombre (str): Nombre de la persona a saludar
        formal (bool, optional): Si el saludo debe ser formal. Defaults to False.
        
    Returns:
        str: Saludo generado
    """
    if formal:
        return f"Estimado/a {nombre}, un placer saludarle."
    return f"¡Hola {nombre}! ¿Cómo estás?"

schema = {
  "name": "saludar",
  "description": "Genera un saludo personalizado",
  "postprocess": True,  # Controla si la IA procesa el resultado
  "parameters": {
    "type": "object",
    "properties": {
      "nombre": {"type": "string", "description": "Nombre de la persona"},
      "formal": {"type": "boolean", "description": "Si el saludo debe ser formal"}
    },
    "required": ["nombre"]
  }
}
```

### Ejemplo Avanzado: Integración con MongoDB

```python
# Ejemplo: tools/get_hotel_info.py

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
    "postprocess": False,
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
```

### Tipos de Herramientas

1. **Herramientas Estáticas**: Definidas en archivos Python en `/tools/`
2. **Herramientas Dinámicas**: Creadas en tiempo de ejecución desde la interfaz
3. **Herramientas Generadas**: Creadas automáticamente por la IA

## 🔒 Seguridad y Consideraciones

- **Aislamiento**: Las herramientas se ejecutan en el mismo contexto que la aplicación
- **Validación**: Los parámetros se validan según el schema antes de la ejecución
- **Credenciales**: Las API keys se almacenan en `.env` y se acceden vía `os.getenv()`
- **Control**: Las herramientas deben estar explícitamente activadas para ser usadas
- **Granularidad**: Control individual de post-procesado por herramienta
- **Logging**: Todas las ejecuciones quedan registradas para auditoría
- **Manejo de errores**: Las excepciones son capturadas y documentadas para evitar fallos en cascada

## 🔍 Solución de Problemas Comunes

### Problemas de Importación de Módulos

Si se encuentran errores como `ModuleNotFoundError: No module named 'X'`:

1. Verificar que la aplicación se ejecuta dentro del entorno virtual correcto
2. Utilizar `python -m streamlit run streamlit_app.py` para asegurar el entorno correcto
3. Comprobar que todas las dependencias están instaladas con `pip install -r requirements.txt`

### Integración con MongoDB y errores de BSON

Los problemas con MongoDB y BSON (como `cannot import name 'SON' from 'bson'`) pueden resolverse:

1. Desinstalando el paquete `bson` independiente: `pip uninstall bson`
2. Usando PyMongo 4.6.1 o superior: `pip install pymongo==4.6.1`
3. Serializando ObjectId y otros tipos BSON mediante:
   ```python
   json.loads(json.dumps(mongo_object, default=str))
   ```
   en lugar de depender de módulos como `bson.json_util`

### Variables de Entorno no Disponibles

Si las variables de entorno no están disponibles para las herramientas:

1. Verificar que existen en el archivo `.env`
2. Usar `env_manager.reload_env_variables()` para cargarlas en tiempo de ejecución
3. Comprobar que se invoca `load_dotenv()` al inicio de cada herramienta que las requiere

## 🚀 Estado Actual y Próximos Pasos

### Implementado

- ✅ Interfaz de chat funcional con modelos GPT-4, GPT-4-Turbo y GPT-3.5-Turbo
- ✅ Panel de administración completo con gestión visual
- ✅ Sistema de herramientas modulares con carga dinámica
- ✅ Integración con MongoDB para herramientas de acceso a datos
- ✅ Creación dinámica de herramientas con UI dedicada
- ✅ Generación automática con IA y detección de variables
- ✅ Control de activación y post-procesado por herramienta
- ✅ Prompts especializados para function calling
- ✅ Interfaz mejorada con paginación y feedback visual
- ✅ Logging multinivel y exportación en múltiples formatos
- ✅ Sistema de diagnóstico avanzado con logs detallados

### En Desarrollo

- 🔄 Persistencia en base de datos (SQLite/PostgreSQL)
- 🔄 Autenticación y control de acceso
- 🔄 Herramienta CLI para gestión
- 🔄 Editor visual de herramientas
- 🔄 Tests unitarios para validación automática

### Planificado

- 📅 Encadenamiento de herramientas (toolchains)
- 📅 Soporte para otros proveedores LLM (Claude, Gemini)
- 📅 Despliegue containerizado (Docker/Kubernetes)
- 📅 Marketplace de herramientas
- 📅 API REST para integración con otros sistemas
- 📅 Agentes autónomos con herramientas auto-evolutivas

---

Este documento define el **contexto técnico y arquitectura global** del proyecto OpenAI Modular MCP. Se recomienda mantenerlo actualizado como referencia base para el desarrollo, documentación técnica e integraciones futuras.