# 🧠 HALion Architecture Overview

> Versión: 1.0  
> Última actualización: 2025-04-14  
> Autor: RGiskard7

## Índice

- [🧠 HALion Architecture Overview](#-halion-architecture-overview)
  - [Índice](#índice)
  - [Visión General](#visión-general)
  - [Principios de Arquitectura](#principios-de-arquitectura)
  - [Estructura de Carpetas](#estructura-de-carpetas)
  - [Descripción de los Módulos](#descripción-de-los-módulos)
    - [`controllers/`](#controllers)
    - [`core/`](#core)
    - [`models/`](#models)
    - [`services/`](#services)
    - [`views/`](#views)
    - [`utils/`](#utils)
    - [`tools/`](#tools)
  - [Flujo de Ejecución](#flujo-de-ejecución)
  - [Convenciones](#convenciones)
  - [Proyección y Escalabilidad](#proyección-y-escalabilidad)
  - [Notas Finales](#notas-finales)

---

## Visión General

HALion es un sistema modular de agentes LLM orientado a la ejecución de herramientas (`tools`) y flujos encadenados (`toolchains`). Está diseñado como una plataforma extensible que combina procesamiento de lenguaje natural con ejecución de funciones personalizadas y gestión asistida por IA.

El objetivo es proporcionar una interfaz de control sobre herramientas definidas por el usuario, con soporte para:

- Llamadas a funciones via OpenAI `function_calling`
- Toolchains dinámicas encadenadas
- Generación de herramientas y flujos con IA
- Registro de llamadas y errores
- Futuro soporte a base de datos y usuarios

---

## Principios de Arquitectura

- **Modularidad**: cada responsabilidad se encuentra en su módulo correspondiente
- **Separación de responsabilidades**: controladores, servicios, vistas, modelos y lógica de negocio están claramente separados
- **Escalabilidad**: preparada para multiusuario, base de datos y expansión de features
- **Legibilidad**: código y rutas autoexplicativas
- **Extensibilidad**: herramientas y flujos pueden añadirse en caliente

---

## Estructura de Carpetas

```bash
app/
│
├── components/              # Componentes visuales reutilizables
│   └── tool_card.py
│
├── config/                  # Configuración persistente (toolchains, status, etc)
│   └── toolchains.json
│
├── controllers/            # Lógica de control entre vista y servicios
│   ├── tools_controller.py
│   └── toolchain_controller.py # Nuevo: Gestiona acciones de UI para toolchains
│
├── core/                    # Núcleo funcional de la aplicación (sin dependencia de vistas)
│   ├── tool_manager.py
│   ├── tool_definition_registry.py # Gestiona registro/archivos .py de tools
│   ├── toolchain_registry.py  # Nuevo: Gestiona registro y persistencia de toolchains
│   ├── logger.py
│   └── env_manager.py
│
├── models/                  # Modelos de datos
│   └── toolchain_model.py
│
├── services/                # Lógica de negocio (servicios independientes)
│   ├── chat_services.py     # Comunicación con OpenAI
│   ├── chat_service.py     # Comunicación con OpenAI
│   └── toolchain_service.py # Nuevo: Ejecución de toolchains y generación AI
│
├── utils/                   # Utilidades varias
│   ├── ai_generation.py
│   └── env_detection.py
│
├── views/                   # Interfaz gráfica (Streamlit)
│   ├── admin_view.py
│   ├── chat_view.py
│   ├── env_view.py
│   ├── logs_view.py
│   ├── tools_view.py
│   └── toolchains_view.py
│
├── tools/                   # Herramientas dinámicas creadas por el usuario
│   └── *.py
│
├── debug_logs/              # Carpeta de logs internos
│   └── *.log
│
└── main.py                  # Punto de entrada de la app
```

---

## Descripción de los Módulos

### `controllers/`

Encapsulan acciones del usuario iniciadas desde la vista. Gestionan el estado de la sesión de Streamlit (`session_state`) relacionado con la acción y actúan como intermediarios hacia los servicios o el núcleo. No deben contener lógica de negocio compleja ni manipular datos directamente (delegan al registro o servicio). Ejemplo: `toolchain_controller.py` maneja los botones de la UI de toolchains.

### `core/` (Núcleo Funcional)

Contiene la lógica central y reutilizable de la aplicación, independiente de la interfaz de usuario.

*   **Nota sobre Nomenclatura (Manager vs. Registry):**
    *   `*_manager`: Generalmente gestiona el estado *en tiempo de ejecución* de un conjunto de elementos (ej. `tool_manager` gestiona si las tools están activas o su estado de postproceso).
    *   `*_registry`: Generalmente gestiona el registro y la persistencia de las *definiciones* de los elementos (ej. `toolchain_registry` maneja la carga/guardado de las definiciones de toolchains; `tool_definition_registry` maneja los archivos `.py` y el registro en memoria de las definiciones de tools).

-Contiene la lógica principal del sistema:
- `tool_manager.py`: carga y gestión del estado runtime de tools (activas, postprocess).
- `tool_definition_registry.py`: registro en memoria de tools dinámicas, y gestión de archivos fuente (.py) de todas las tools (lectura, escritura, borrado).

*   **`tool_manager.py`**: Orquestador central para el estado *runtime* de las herramientas. Carga las definiciones (usando `tool_definition_registry` implícitamente al cargar archivos), gestiona qué herramientas están activas (`is_tool_active`) y su configuración de postproceso (`get_tool_postprocess`) leyendo/escribiendo en `.tool_status.json`. Proporciona la lista de herramientas utilizables (`get_tools`) y permite ejecutarlas (`call_tool_by_name`).
*   **`tool_definition_registry.py`**: Gestiona las *definiciones* y la *persistencia* de las herramientas individuales. Mantiene un registro en memoria de las herramientas dinámicas (`dynamic_tools`) y proporciona funciones para leer (`get_tool_code`), escribir (`save_tool_code`, `persist_tool_to_disk`) y eliminar (`delete_tool_file`) los archivos `.py` que definen las herramientas en la carpeta `tools/`. También registra la función y schema en memoria (`register_tool`).
*   **`toolchain_registry.py`**: Gestiona las *definiciones* y la *persistencia* de las cadenas de herramientas (toolchains). Carga (`load_toolchains_from_disk`) y guarda (`save_toolchains_to_disk`) las definiciones desde/hacia `toolchains.json`. Mantiene un registro en memoria (`_toolchain_registry`) de las definiciones disponibles.
*   `logger.py`: registros de llamadas
*   `env_manager.py`: variables de entorno

### `models/`

Estructuras de datos simples y fuertemente tipadas, actualmente solo incluye:

- `Toolchain`
- `ToolchainStep`

Futuro: aquí se colocarán modelos persistentes con SQLAlchemy / Pydantic.

### `services/` (Lógica de Negocio)

Contiene la lógica de negocio y flujos complejos, desacoplados de la UI y del núcleo base.

- `chat_services.py`: gestiona la interacción con OpenAI (incluyendo `function_calling` para tools individuales).
- `chat_service.py`: gestiona la interacción con OpenAI (incluyendo `function_calling` para tools individuales).
- `toolchain_service.py`: encapsula la lógica para ejecutar una toolchain paso a paso y para orquestar la generación de toolchains mediante IA.

*   **`chat_service.py`**: Servicio responsable de la comunicación con la API de OpenAI para el chat conversacional. Prepara los mensajes, incluye las herramientas activas (obtenidas de `tool_manager`) para `function_calling`, procesa la respuesta del modelo, y ejecuta las herramientas individuales solicitadas por el LLM.
*   **`toolchain_service.py`**: Contiene la lógica para ejecutar una *secuencia* de herramientas definida en una toolchain. Obtiene la definición de la toolchain (de `toolchain_registry`), obtiene las herramientas necesarias (de `tool_manager`), ejecuta los pasos secuencialmente pasando el contexto, y devuelve el resultado final. También orquesta la generación de definiciones de toolchains usando IA (llamando a `utils/ai_generation`).
- `tool_service.py`: encapsula la lógica para generar tools con IA y gestionar sus variables de entorno.

*   **`tool_service.py`**: Servicio enfocado en la creación asistida de herramientas individuales. Orquesta la generación de código de tool mediante IA (llamando a `utils/ai_generation`), extrae metadatos (schema, nombre) y detecta variables de entorno necesarias (llamando a `utils/env_detection`), y gestiona el guardado de estas variables (llamando a `core/env_manager`). También puede incluir lógica para la persistencia y registro coordinado de nuevas herramientas (interactuando con `tool_definition_registry` y `tool_manager`).

A futuro aquí se añadirá lógica de autenticación, servicios de usuario, métricas, auditoría, etc.

### `views/`

Responsables del renderizado de interfaz con Streamlit. Solo deben llamar a `controllers` o `services`, nunca a `core` directamente.

### `utils/`

Funciones auxiliares desacopladas:

- `ai_generation.py`: generación de código con IA
- `env_detection.py`: detección de claves y entornos en texto

### `tools/`

Contiene herramientas dinámicas definidas por el usuario. Se almacenan como scripts `.py` que se cargan en caliente.

---

## Flujo de Ejecución

1. `main.py` inicia y configura Streamlit
2. El usuario navega a una vista (por ejemplo, `tools_view`)
3. La vista invoca funciones de `tools_controller`
4. El controlador accede a `tool_manager` o `tool_definition_registry`
5. Se actualiza el estado de la sesión
6. El resultado se renderiza visualmente con un componente (`tool_card`)

---

## Convenciones

- Todos los nombres en `snake_case`
- Todos los ficheros de tools dinámicas deben coincidir con su `schema["name"]`
- Las herramientas deben tener:
  - Una función llamable con docstring y typing
  - Un `schema` JSON válido compatible con OpenAI
- Los logs se almacenan en `debug_logs/`
- La configuración de herramientas activas está en `config/.tool_status.json`
- Toolchains en `config/toolchains.json`

---

## Proyección y Escalabilidad

- ✅ Modularización ya lista
- 🔜 Base de datos relacional con SQLAlchemy (estructura ya preparada en `models/`)
- 🔜 Gestión multiusuario (autenticación, permisos)
- 🔜 Soporte multi-toolchain, planificador inteligente
- 🔜 Versionado de herramientas
- 🔜 Importación/exportación visual de toolchains
- 🔜 API REST paralela para integración con apps externas (Flask/FastAPI)
- 🔜 Separación backend/frontend completa (si se desea)

---

## Notas Finales

Esta arquitectura está diseñada para ser mantenible y ampliable. Todas las decisiones siguen principios de Clean Architecture, inspiradas en MVC, y están pensadas para facilitar el trabajo colaborativo, pruebas unitarias y escalabilidad futura.