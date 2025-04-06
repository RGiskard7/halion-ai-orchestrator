# OpenAI Modular MCP Framework

Este proyecto es un sistema modular estilo MCP (Model Context Protocol) como el propuesto por Claude, pero implementado con la API de OpenAI. Está diseñado para gestionar herramientas externas (tools) que GPT puede usar mediante function calling. 

Incluye:
- Gestión dinámica de herramientas (tools) desde archivos o interfaz web.
- Panel de administración con login y sesiones.
- Permisos por usuario.
- Logs de llamadas a tools.
- Creación, edición y eliminación de tools desde la UI.
- Guardado de tools en disco como `.py` y `.yaml`.

---

## 📦 Requisitos

- Python 3.9 o superior
- Una clave de API de OpenAI

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tuusuario/openai_modular_mcp.git
cd openai_modular_mcp
```

### 2. Crear y activar un entorno virtual (recomendado)

```bash
# Crear el entorno virtual\python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en macOS/Linux
source venv/bin/activate
```

### 3. Configurar las variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` y añade tu clave de OpenAI:

```env
OPENAI_API_KEY=sk-...
AUTH_SECRET=supersecret
```

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar el servidor

```bash
uvicorn main:app --reload
```

---

## 🧪 Uso básico

1. Abre el navegador: [http://localhost:8000](http://localhost:8000)
2. Inicia sesión como:
   - **Usuario**: `edu`
   - **Contraseña**: `clave123`
3. Escribe un mensaje como “¿Qué clima hace en Madrid?”
4. GPT responderá invocando la tool `get_weather` si corresponde

---

## 🔐 Panel de Administración

Accede a [http://localhost:8000/admin](http://localhost:8000/admin)

### Funcionalidades:
- Ver usuarios y sus tools asignadas
- Crear y eliminar usuarios
- Ver tools estáticas y dinámicas
- Crear nuevas tools desde la web
- Editar o eliminar tools
- Ver logs de llamadas a herramientas
- Ver errores de carga de plugins mal formados
- Recargar tools sin reiniciar el servidor

---

## 🧰 Crear nueva Tool (desde la UI)

1. Nombre: `decir_hora`
2. Descripción: `Devuelve la hora actual`
3. JSON Schema:

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

4. Código Python:

```python
from datetime import datetime

def decir_hora():
    return f"Son las {datetime.now().strftime('%H:%M:%S')}"
```

✅ La tool se guarda automáticamente en `tools/decir_hora.py` y se carga al instante tras hacer clic en “🔄 Recargar tools”.

---

## 🧹 Eliminar una Tool

1. En la lista de tools del panel admin, haz clic en ❌ Eliminar
2. Confirma la eliminación

✅ El archivo `.py` será borrado de la carpeta `tools/`

---

## ✏️ Editar una Tool existente

1. En la lista de tools del admin, haz clic en ✏️ Editar
2. Modifica el código o el schema JSON
3. Haz clic en “💾 Guardar Cambios”
4. Se sobrescribe el `.py` y se guarda `.yaml` con el schema

---

## 📄 Archivos importantes

- `main.py`: servidor FastAPI y rutas
- `executor.py`: orquestador de llamadas con GPT
- `tool_manager.py`: carga de tools desde disco y memoria
- `dynamic_tool_registry.py`: creación/edición dinámica
- `auth.py`: login y usuarios
- `templates/`: plantillas HTML para chat y admin
- `tools/`: carpeta donde viven todas las tools
- `tool_calls.log`: registro de herramientas usadas

---

## 📚 Añadir una tool manualmente (archivo `.py`)

```python
# tools/saludar.py

def saludar(nombre: str) -> str:
    return f"Hola, {nombre}, ¿cómo estás?"

schema = {
    "name": "saludar",
    "description": "Saluda a una persona por su nombre",
    "parameters": {
        "type": "object",
        "properties": {
            "nombre": {"type": "string", "description": "Nombre de la persona"}
        },
        "required": ["nombre"]
    }
}
```

---

## ⚠️ Errores de carga

- Si un archivo `.py` no contiene `schema` o una función válida, se muestra en el panel de errores.
- Puedes eliminar, corregir y volver a recargar sin reiniciar el servidor.

---

## 🧪 Pruebas rápidas

```bash
curl -X POST http://localhost:8000/chat-ui -F "prompt=¿Qué clima hace en Madrid?"
```

---

## 💡 Siguientes pasos sugeridos

- Soporte para tests unitarios de cada tool
- Permitir toolchains (encadenamiento)
- Guardar todo en SQLite o PostgreSQL
- Editor visual de tools sin código
- CLI para gestionar tools desde terminal

---

## 📬 Contacto

Desarrollado por Edu ✨

---

Listo para usar, extender y convertir en tu entorno modular de IA personal.
