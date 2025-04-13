# Refactorización del Proyecto OpenAI Modular MCP

Este documento describe la refactorización del proyecto para mejorar su estructura, mantenibilidad y escalabilidad.

## Estructura de Carpetas

La nueva estructura del proyecto está organizada de la siguiente manera:

```
/app
  /components      # Componentes de UI reutilizables
    - tool_card.py      # Componente para mostrar herramientas
    - __init__.py
  /controllers     # Controladores que gestionan la lógica de negocio
    - tools_controller.py  # Controlador para herramientas
    - __init__.py
  /core            # Núcleo funcional reutilizable
    - executor.py          # Ejecutor de herramientas con OpenAI
    - tool_manager.py      # Gestor de herramientas
    - dynamic_tool_registry.py # Registro de herramientas dinámicas
    - env_manager.py       # Gestor de variables de entorno
    - logger.py            # Sistema de logs
    - __init__.py
  /models          # Modelos de datos (actualmente vacío, para futura expansión)
    - __init__.py
  /utils           # Funciones de utilidad
    - ai_generation.py    # Generación de código con IA
    - env_detection.py    # Detección de variables de entorno
    - __init__.py
  /views           # Vistas de la interfaz de usuario
    - chat_view.py        # Vista de chat
    - admin_view.py       # Vista de administración
    - tools_view.py       # Vista de herramientas
    - env_view.py         # Vista de variables de entorno
    - logs_view.py        # Vista de logs
    - __init__.py
  main.py          # Punto de entrada principal
  __init__.py
run.py            # Script para ejecutar la aplicación
```

## Patrones de Diseño Aplicados

### Patrón MVC (adaptado a Streamlit)

- **Modelo (models)**: Estructuras de datos y lógica para acceder a ellos
- **Vista (views)**: Interfaz de usuario dividida en componentes reutilizables
- **Controlador (controllers)**: Lógica de negocio que conecta las vistas con los modelos

### Principio de Responsabilidad Única (SRP)

- Cada clase y módulo tiene una única razón para cambiar
- Los componentes están separados según su función

### Principio de Abstracción de Interfaces (ISP)

- Las interfaces están divididas en componentes pequeños y específicos
- Los componentes dependen solo de las interfaces que realmente utilizan

## Mejoras Realizadas

### 1. Modularización
- El archivo `streamlit_app.py` (1300+ líneas) se ha dividido en múltiples archivos más pequeños y manejables
- Cada módulo tiene una responsabilidad clara y única

### 2. Separación del Core
- Los componentes centrales están aislados en `/core`, lo que facilita su reutilización en otros proyectos
- No hay dependencias directas entre el core y la interfaz de usuario

### 3. Componentes Reutilizables
- Se han creado componentes UI reutilizables (ej: `tool_card.py`)
- Facilita mantener consistencia visual y reducir duplicación de código

### 4. Mejora de Mantenibilidad
- Cada archivo es más pequeño y fácil de entender
- Las dependencias entre módulos están claramente definidas

### 5. Preparación para Escalabilidad
- La estructura permite añadir nuevas funcionalidades sin modificar el código existente
- La carpeta `/models` está preparada para una posible expansión con modelos de datos

## Cómo Ejecutar el Proyecto

### Método 1: Script Directo
```bash
python run.py
```

### Método 2: Streamlit Directo
```bash
streamlit run app/main.py
```

## Consideraciones Futuras

- **Sistema de plugins**: La estructura actual facilita la implementación de un sistema de plugins para extender funcionalidades
- **API REST**: El core podría exponerse como una API REST para ser consumido por otras aplicaciones
- **Pruebas unitarias**: La separación clara de responsabilidades facilita la creación de pruebas unitarias 