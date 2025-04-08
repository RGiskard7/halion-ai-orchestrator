# 🧩 OpenAI Modular MCP - Documentación Técnica

## 📄 Visión General

OpenAI Modular MCP (Model-Context-Protocol) es una plataforma extensible para la creación, gestión y despliegue de asistentes IA con capacidades personalizadas a través de herramientas modulares. El sistema implementa un enfoque arquitectónico que permite a los modelos de lenguaje de OpenAI interactuar con funciones externas de forma estructurada y administrada.

> Este documento proporciona una visión técnica completa del proyecto, su arquitectura, componentes y flujos de trabajo.

## 🎯 Objetivos del Proyecto

- **Extensibilidad**: Proporcionar una base robusta para construir asistentes IA personalizados
- **Modularidad**: Permitir la adición, modificación y eliminación de capacidades sin afectar al sistema central
- **Usabilidad**: Ofrecer una interfaz intuitiva tanto para usuarios finales como para administradores
- **Transparencia**: Registrar todas las interacciones y ejecuciones para análisis y auditoría
- **Seguridad**: Implementar buenas prácticas para el manejo de credenciales y ejecución de código

## 🏗️ Arquitectura del Sistema

### Diagrama de Flujo Principal

```
Usuario → Interfaz Streamlit → Executor (chat_with_tools) → OpenAI API
                                       ↓
                                  ¿function_call?
                                       ↓
                                     Si → Tool Manager → Herramienta Específica
                                       ↓                      ↓
                                    Logger ← ← ← ← ← ← ← Resultado
                                       ↓
                                   Respuesta → Usuario
```

### Componentes Principales

#### 1. `streamlit_app.py`

Interfaz de usuario construida con Streamlit que proporciona:

- **Chat con IA**: Interfaz conversacional con soporte para texto e imágenes
  - Selección de modelo (GPT-4, GPT-3.5, etc.)
  - Control de temperatura para ajustar creatividad
  - Historial de conversación persistente

- **Panel de Administración**:
  - Gestión de herramientas (carga, recarga, creación)
  - Visualización y exportación de logs
  - Administración de variables de entorno

#### 2. `executor.py`

Orquestador central que:

- Construye los mensajes para la API de OpenAI
- Incluye las definiciones de herramientas disponibles
- Procesa la respuesta y detecta llamadas a funciones
- Ejecuta las herramientas solicitadas y reincorpora los resultados

#### 3. `tool_manager.py`

Gestor de herramientas que:

- Carga dinámicamente todas las herramientas desde el directorio `/tools/`
- Mantiene un registro de herramientas activas/inactivas
- Registra errores de carga para diagnóstico
- Proporciona acceso unificado a herramientas estáticas y dinámicas

#### 4. `dynamic_tool_registry.py`

Registro de herramientas dinámicas que:

- Permite definir herramientas en tiempo de ejecución
- Compila código Python desde la interfaz de usuario
- Persiste herramientas creadas dinámicamente a disco
- Gestiona el ciclo de vida de herramientas en memoria

#### 5. `logger.py`

Sistema de registro que:

- Documenta cada ejecución de herramienta
- Almacena metadatos, argumentos y resultados
- Proporciona funciones para exportar logs
- Facilita el análisis y depuración

#### 6. `env_manager.py`

Gestor de variables de entorno que:

- Lee y escribe en el archivo `.env`
- Permite añadir, modificar y eliminar variables
- Protege información sensible como API keys

## 🔄 Flujos de Trabajo

### 1. Flujo de Conversación

1. El usuario envía un mensaje a través de la interfaz de chat
2. `streamlit_app.py` llama a `chat_with_tools()` en `executor.py`
3. `executor.py` prepara el contexto y envía la solicitud a OpenAI
4. OpenAI determina si se necesita invocar una herramienta
5. Si es necesario, `executor.py` obtiene la herramienta de `tool_manager.py`
6. Se ejecuta la herramienta y se registra la operación en `logger.py`
7. El resultado se incorpora a la respuesta y se muestra al usuario

### 2. Flujo de Gestión de Herramientas

#### Carga Inicial:

1. Al iniciar la aplicación, `tool_manager.py` escanea el directorio `/tools/`
2. Cada archivo Python se importa y se registra su función principal y esquema
3. Se cargan las herramientas dinámicas previamente guardadas
4. Se aplica el estado de activación según `.tool_status.json`

#### Creación Dinámica:

1. El administrador define una nueva herramienta en la interfaz
2. `dynamic_tool_registry.py` compila y registra la función
3. La herramienta está disponible inmediatamente sin reiniciar
4. Opcionalmente, se persiste a disco como un archivo Python

## 📂 Estructura de Directorios

```
.
├── tools/                      # Herramientas disponibles
│   ├── buscar_en_internet.py   # Búsqueda web (DuckDuckGo)
│   ├── get_current_weather.py  # Información meteorológica
│   ├── saludar.py              # Ejemplo simple
│   └── send_email.py           # Envío de correos
├── streamlit_app.py            # Aplicación principal
├── executor.py                 # Orquestador de OpenAI
├── tool_manager.py             # Gestión de herramientas
├── dynamic_tool_registry.py    # Registro dinámico
├── logger.py                   # Sistema de logs
├── env_manager.py              # Gestión de .env
├── .env.example                # Plantilla de variables
├── .tool_status.json           # Estado de activación
├── requirements.txt            # Dependencias
└── README.md                   # Documentación general
```

## 🔌 Integración de Herramientas

### Anatomía de una Herramienta

Cada herramienta consta de dos componentes principales:

1. **Función Python**: Implementa la lógica de la herramienta
2. **Esquema JSON**: Define la interfaz y parámetros

```python
# Ejemplo: tools/saludar.py

def saludar(nombre, formal=False):
    if formal:
        return f"Estimado/a {nombre}, un placer saludarle."
    return f"¡Hola {nombre}! ¿Cómo estás?"

schema = {
  "name": "saludar",
  "description": "Genera un saludo personalizado",
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

### Tipos de Herramientas

1. **Herramientas Estáticas**: Definidas en archivos Python en `/tools/`
2. **Herramientas Dinámicas**: Creadas en tiempo de ejecución desde la interfaz

## 🔒 Seguridad y Consideraciones

- **Aislamiento**: Las herramientas se ejecutan en el mismo contexto que la aplicación
- **Validación**: Los parámetros se validan según el esquema antes de la ejecución
- **Credenciales**: Las API keys se almacenan en `.env` y se acceden vía `os.getenv()`
- **Logging**: Todas las ejecuciones quedan registradas para auditoría

## 🚀 Estado Actual y Próximos Pasos

### Implementado

- ✅ Interfaz de chat funcional con modelos GPT-3.5 y GPT-4
- ✅ Soporte para GPT-4-Vision (procesamiento de imágenes)
- ✅ Panel de administración completo
- ✅ Sistema de herramientas modulares
- ✅ Creación dinámica de herramientas
- ✅ Logging y exportación

### En Desarrollo

- 🔄 Persistencia en base de datos (SQLite/PostgreSQL)
- 🔄 Autenticación y control de acceso
- 🔄 Herramienta CLI para gestión
- 🔄 Editor visual de herramientas

### Planificado

- 📅 Encadenamiento de herramientas (toolchains)
- 📅 Soporte para otros proveedores LLM
- 📅 Despliegue containerizado (Docker/Kubernetes)
- 📅 Marketplace de herramientas

---

Este documento define el **contexto técnico y arquitectura global** del proyecto OpenAI Modular MCP. Se recomienda mantenerlo actualizado como referencia base para el desarrollo, documentación técnica e integraciones futuras.