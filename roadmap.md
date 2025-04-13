# 🗺️ Hoja de Ruta - HALion: Modular Intelligence Orchestrator

Este documento traza el camino evolutivo del proyecto, ordenado por prioridad y categoría. Sirve como guía para futuras mejoras, funcionalidades deseadas y mantenibilidad a largo plazo.

---

## ✅ Mínimo Producto Viable (completado)

- [x] Interfaz Streamlit con chat y panel de administración
- [x] Invocación de tools vía OpenAI function calling
- [x] Tools estáticas en `/tools/*.py` y tools dinámicas desde UI
- [x] Logs detallados de llamadas a tools
- [x] Edición de variables de entorno `.env` desde la UI
- [x] Activación selectiva de tools desde `.tool_status.json`

---

## 🧩 Nuevas funcionalidades

### 1. Tools encadenadas (Toolchains)
- Permitir que el resultado de una tool active otra
- Ejemplo: buscar -> analizar texto -> generar resumen

### 2. Validación automática de JSON Schema
- Validar que las tools tengan un schema bien formado
- Detectar conflictos o tipos incompatibles

### 3. Test unitarios para cada tool
- Framework simple para testear tools desde UI
- Output esperado vs resultado real

### 4. Soporte multillamada (function_call continua)
- Permitir que GPT encadene varias llamadas a tools sin intervención humana

### 5. Persistencia en base de datos
- Reemplazar logs y tool_status con SQLite o PostgreSQL
- Guardar usuarios, sesiones, tools, estadísticas

### 6. Soporte de imágenes con GPT-4-Vision
- Implementar subida de imágenes desde la UI
- Procesamiento visual usando GPT-4-Vision
- Herramientas específicas para análisis de imágenes

---

## 🔒 Seguridad y control de usuarios

- Login completo con roles (admin, usuario)
- Permisos por tool
- Historial de uso por usuario
- Sesiones temporales o persistentes

---

## ⚙️ Dev Tools & CLI

- CLI para registrar tools desde terminal
- CLI para ejecutar tools a mano sin usar GPT
- Recargar tools desde terminal

---

## 🧠 Editor visual de tools

- Interfaz drag-and-drop para crear JSON schema
- Campos de ejemplo, validaciones en vivo
- Vista previa de salida esperada
- Incluir ejemplos de código autogenerado

---

## 🔄 Backend API REST (FastAPI)

- Exponer endpoints para:
  - Consultar tools disponibles
  - Ejecutar tools directamente vía HTTP
  - Registrar nuevas tools (POST /tools)

---

## 🪄 Interacción avanzada GPT

- Instrucciones personalizadas por usuario (sistema)
- Memoria de contexto prolongada (vector store opcional)
- Historial de conversaciones guardado

---

## 🧱 Infraestructura y despliegue

- Contenedor Docker con todo el entorno
- Deploy en Render, Railway o Heroku
- Sistema de logs externo (Logtail, Sentry, etc.)

---

## 🎯 Integraciones futuras

- Webhooks para ejecutar tools desde eventos externos
- Bot en Telegram que use las tools activas
- Extensión para VS Code o Notion

---

## 🔚 Meta

- Documentación completa para usuarios y desarrolladores
- Plantilla de tools para compartir/exportar
- Plugin system (cargar herramientas desde GitHub repos externos)

---

> Esta hoja de ruta está viva. Puedes reorganizar prioridades según necesidades o inspiración.

¡Vamos a modularizar el futuro! 🧠✨