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
│   └── toolchain_controller.py
│
├── core/                    # Núcleo funcional de la aplicación (sin dependencia de vistas)
│   ├── tool_manager.py
│   ├── dynamic_tool_registry.py
│   ├── toolchain_loader.py
│   ├── logger.py
│   └── env_manager.py
│
├── models/                  # Modelos de datos
│   └── toolchain_model.py
│
├── services/                # Lógica de negocio (servicios independientes)
│   └── chat_services.py     # Comunicación con OpenAI + ejecución de toolchains
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

Encapsulan acciones del usuario. Gestionan el estado de Streamlit (`session_state`) y actúan como capa de mediación entre vistas y lógica de negocio. No deben tener lógica compleja ni manipular datos directamente.

### `core/`

Contiene la lógica principal del sistema:

- `tool_manager.py`: carga y ejecución de tools
- `dynamic_tool_registry.py`: tools dinámicas en memoria
- `logger.py`: registros de llamadas
- `env_manager.py`: variables de entorno
- `toolchain_loader.py`: carga y parsing de toolchains desde JSON

### `models/`

Estructuras de datos simples y fuertemente tipadas, actualmente solo incluye:

- `Toolchain`
- `ToolchainStep`

Futuro: aquí se colocarán modelos persistentes con SQLAlchemy / Pydantic.

### `services/`

Contiene la lógica de negocio y flujos. Actualmente:

- `chat_services.py`: ejecuta tools, interactúa con OpenAI y toolchains

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
4. El controlador accede a `tool_manager` o `dynamic_tool_registry`
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