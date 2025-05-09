# 🛠️ Guía de Desarrollo de Herramientas (Tools) para HALion

## Índice

1.  [Introducción](#1-introducción)
2.  [Requisitos Previos](#2-requisitos-previos)
3.  [Anatomía de una Herramienta HALion](#3-anatomía-de-una-herramienta-halion)
    *   [Archivo Python (`.py`)](#archivo-python-py)
    *   [Función Principal](#función-principal)
    *   [Schema JSON](#schema-json)
4.  [Ubicación de las Herramientas](#4-ubicación-de-las-herramientas)
5.  [Convenciones de Nomenclatura](#5-convenciones-de-nomenclatura)
6.  [Paso a Paso: Creando una Nueva Herramienta](#6-paso-a-paso-creando-una-nueva-herramienta)
    *   [Definir Propósito y Funcionalidad](#definir-propósito-y-funcionalidad)
    *   [Crear el Archivo `.py`](#crear-el-archivo-py)
    *   [Implementar la Función Python](#implementar-la-función-python)
    *   [Definir el Schema JSON](#definir-el-schema-json)
    *   [Manejo de Variables de Entorno](#manejo-de-variables-de-entorno)
7.  [Ejemplos de Herramientas](#7-ejemplos-de-herramientas)
    *   [Ejemplo 1: Herramienta Simple (`saludar`)](#ejemplo-1-herramienta-simple-saludar)
    *   [Ejemplo 2: Herramienta Avanzada (`obtener_clima`)](#ejemplo-2-herramienta-avanzada-obtener_clima)
8.  [Registro y Activación de Herramientas](#8-registro-y-activación-de-herramientas)
9.  [Buenas Prácticas de Desarrollo](#9-buenas-prácticas-de-desarrollo)
10. [Generación de Herramientas con IA](#10-generación-de-herramientas-con-ia)
11. [Solución de Problemas Comunes](#11-solución-de-problemas-comunes)

---

## 1. Introducción

Las herramientas (o "tools") son el corazón de la extensibilidad de HALion. Permiten que los modelos de lenguaje (LLMs) interactúen con el mundo exterior, ejecuten código personalizado, accedan a APIs, bases de datos, o realicen cualquier tarea que puedas programar en Python.

Esta guía te mostrará cómo desarrollar tus propias herramientas para HALion, desde las más simples hasta integraciones más complejas.

## 2. Requisitos Previos

*   Conocimiento sólido de **Python 3**.
*   Comprensión básica de **JSON** para la definición de schemas.
*   Familiaridad con el uso de **variables de entorno** (opcional, pero común para APIs).
*   Un entorno de desarrollo HALion configurado.

## 3. Anatomía de una Herramienta HALion

Cada herramienta en HALion se compone de dos partes fundamentales, ambas contenidas (o referenciadas) dentro de un único archivo Python:

1.  Una **función Python** que implementa la lógica de la herramienta.
2.  Un **diccionario `schema` JSON** que describe la herramienta al LLM y a HALion.

### Archivo Python (`.py`)

Cada herramienta reside en su propio archivo `.py` dentro del directorio `app/tools/`. Por ejemplo, una herramienta para saludar se podría llamar `saludar.py`.

### Función Principal

Esta es la función que HALion ejecutará cuando el LLM decida usar tu herramienta.

*   **Nombre de la Función:** Debe ser descriptivo y, por convención, coincidir con el nombre del archivo (sin la extensión `.py`) y el `name` en el schema.
*   **Argumentos:**
    *   Deben estar claramente definidos con **tipado de Python** (`type hints`).
    *   Se recomienda incluir **docstrings** para cada argumento, explicando su propósito. El LLM usará estas descripciones.
*   **Lógica de la Herramienta:** Aquí implementas lo que la herramienta hace. Puede ser desde un cálculo simple hasta llamadas a APIs externas.
*   **Valor de Retorno:**
    *   La función debe devolver un valor. Este valor será enviado de vuelta al LLM (si `postprocess` es `True`) o directamente al usuario.
    *   Es crucial usar **tipado de Python** para el valor de retorno y, si es posible, un docstring que describa lo que se devuelve.
*   **Docstring de la Función:** El docstring general de la función es muy importante. El LLM lo utiliza para entender qué hace la herramienta y cuándo usarla. ¡Sé claro y conciso!

```python
# Ejemplo de estructura de función
def mi_herramienta_ejemplo(parametro1: str, parametro2: int = 0) -> dict:
    """
    Esta es una descripción clara de lo que hace mi_herramienta_ejemplo.
    El LLM usará esto para decidir si debe llamar a esta función.

    Args:
        parametro1 (str): Descripción del primer parámetro.
        parametro2 (int, optional): Descripción del segundo parámetro. Por defecto es 0.

    Returns:
        dict: Un diccionario con los resultados de la operación.
    """
    # Lógica de la herramienta aquí
    resultado = {"info": f"Procesado: {parametro1}", "valor": parametro2 * 2}
    return resultado
```

### Schema JSON

El `schema` es un diccionario Python que sigue la estructura esperada por OpenAI para la descripción de funciones (function calling). HALion usa este schema para:

*   Informar al LLM sobre la existencia y capacidad de la herramienta.
*   Validar los parámetros proporcionados por el LLM.
*   Gestionar la herramienta en la interfaz de administración.

Componentes clave del `schema`:

*   **`name` (str):** El nombre de la herramienta. **Debe coincidir exactamente** con el nombre de la función Python y el nombre del archivo (sin `.py`).
*   **`description` (str):** Una descripción clara y concisa de lo que hace la herramienta. El LLM se basa fundamentalmente en esta descripción para decidir si utiliza la herramienta.
*   **`postprocess` (bool):**
    *   `True`: El resultado de la herramienta se enviará de vuelta al LLM para que genere una respuesta final en lenguaje natural basada en ese resultado.
    *   `False`: El resultado de la herramienta se mostrará directamente al usuario, sin pasar por el LLM para una elaboración adicional.
*   **`parameters` (dict):** Describe los parámetros que la función acepta.
    *   **`type` (str):** Siempre debe ser `"object"`.
    *   **`properties` (dict):** Un diccionario donde cada clave es el nombre de un parámetro de la función. El valor es otro diccionario que describe ese parámetro:
        *   **`type` (str):** El tipo de dato del parámetro (ej: `"string"`, `"integer"`, `"boolean"`, `"number"`, `"array"`, `"object"`). Debe ser compatible con los tipos JSON.
        *   **`description` (str):** Descripción detallada del parámetro, para que el LLM sepa qué valor enviar.
        *   **`enum` (list, opcional):** Si el parámetro solo puede tomar un conjunto específico de valores.
    *   **`required` (list):** Una lista de strings con los nombres de los parámetros que son obligatorios.

```python
# Ejemplo de schema
schema = {
  "name": "mi_herramienta_ejemplo",
  "description": "Esta es una descripción clara de lo que hace mi_herramienta_ejemplo.",
  "postprocess": True,
  "parameters": {
    "type": "object",
    "properties": {
      "parametro1": {
        "type": "string",
        "description": "Descripción del primer parámetro."
      },
      "parametro2": {
        "type": "integer",
        "description": "Descripción del segundo parámetro. Por defecto es 0."
      }
    },
    "required": ["parametro1"]  # parametro2 es opcional según la firma de la función
  }
}
```

## 4. Ubicación de las Herramientas

Todas las herramientas personalizadas deben ubicarse en el directorio:

`app/tools/`

HALion escanea este directorio al inicio para cargar todas las herramientas disponibles.

## 5. Convenciones de Nomenclatura

Para asegurar que HALion pueda descubrir y registrar correctamente tus herramientas, sigue estas convenciones:

1.  **Nombre del Archivo:** `nombre_de_la_herramienta.py` (snake_case).
2.  **Nombre de la Función Python:** `nombre_de_la_herramienta` (debe ser el mismo que el nombre del archivo sin la extensión).
3.  **Nombre en el Schema (`"name"`):** `"nombre_de_la_herramienta"` (debe ser el mismo que el nombre de la función).

Ejemplo:
*   Archivo: `app/tools/calcular_imc.py`
*   Función: `def calcular_imc(...):`
*   Schema: `schema = {"name": "calcular_imc", ...}`

## 6. Paso a Paso: Creando una Nueva Herramienta

### Definir Propósito y Funcionalidad

Antes de escribir código, ten claro:
*   ¿Qué problema resolverá la herramienta?
*   ¿Qué entradas necesita?
*   ¿Qué salida producirá?
*   ¿Debería el LLM procesar la salida (`postprocess: True`) o debería mostrarse directamente (`postprocess: False`)?

### Crear el Archivo `.py`

Crea un nuevo archivo Python en el directorio `app/tools/`. Por ejemplo, `mi_nueva_herramienta.py`.

### Implementar la Función Python

Escribe la función principal, siguiendo las recomendaciones de la sección "Anatomía de una Herramienta".

```python
# app/tools/mi_nueva_herramienta.py

def mi_nueva_herramienta(input_texto: str, veces: int = 1) -> str:
    """
    Repite un texto un número específico de veces.

    Args:
        input_texto (str): El texto a repetir.
        veces (int, optional): Cuántas veces repetir el texto. Por defecto es 1.

    Returns:
        str: El texto repetido.
    """
    if not isinstance(input_texto, str):
        raise TypeError("El input_texto debe ser un string.")
    if not isinstance(veces, int) or veces < 0:
        raise ValueError("El número de veces debe ser un entero no negativo.")

    return (input_texto + " ") * veces

# El schema se definirá a continuación
```

**Consideraciones Adicionales:**

*   **Imports:** Añade cualquier import necesario al principio del archivo.
*   **Manejo de Errores:** Utiliza bloques `try-except` para capturar excepciones y, si es posible, devuelve mensajes de error informativos. Si una herramienta falla con una excepción no controlada, HALion lo registrará, pero es mejor manejar los errores de forma controlada.
*   **Logging:** Puedes usar el módulo `logging` de Python si necesitas registrar información detallada durante la ejecución de tu herramienta.
*   **Stateless:** Intenta que tus herramientas sean *stateless* (sin estado). Es decir, su salida solo debe depender de sus entradas actuales. Si necesitas persistencia, considera usar bases de datos o archivos externos.

### Definir el Schema JSON

Añade el diccionario `schema` al final de tu archivo `.py`.

```python
# ... (continuación de app/tools/mi_nueva_herramienta.py)

schema = {
  "name": "mi_nueva_herramienta",
  "description": "Repite un texto un número específico de veces. Útil para enfatizar o generar patrones de texto simples.",
  "postprocess": True, # Queremos que el LLM probablemente comente sobre el texto repetido
  "parameters": {
    "type": "object",
    "properties": {
      "input_texto": {
        "type": "string",
        "description": "El texto que se va a repetir."
      },
      "veces": {
        "type": "integer",
        "description": "El número de veces que se repetirá el texto. Debe ser no negativo."
      }
    },
    "required": ["input_texto"] # 'veces' es opcional ya que tiene un valor por defecto en la función
  }
}
```

### Manejo de Variables de Entorno

Si tu herramienta necesita acceder a APIs externas o servicios que requieren claves API u otras configuraciones sensibles:

1.  **Usa el archivo `.env`:** Almacena tus credenciales en el archivo `.env` en la raíz del proyecto HALion.
    ```env
    MI_API_KEY="tu_clave_secreta"
    OTRA_CONFIG="valor_config"
    ```
2.  **Carga las variables en tu herramienta:** Usa la librería `python-dotenv` (que ya debería ser una dependencia de HALion) y `os.getenv`.

```python
# app/tools/herramienta_con_api.py
import os
from dotenv import load_dotenv
import requests # Ejemplo de librería para llamar a una API

# Cargar variables de entorno del archivo .env
load_dotenv()

API_KEY = os.getenv("MI_SERVICIO_API_KEY")
API_ENDPOINT = "https://api.ejemplo.com/data"

def obtener_datos_servicio(parametro_busqueda: str) -> dict:
    """
    Obtiene datos de un servicio externo usando una API Key.

    Args:
        parametro_busqueda (str): Término para buscar en el servicio externo.

    Returns:
        dict: Los datos obtenidos del servicio o un mensaje de error.
    """
    if not API_KEY:
        return {"error": "API Key no configurada. Revisa las variables de entorno."}

    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        params = {"query": parametro_busqueda}
        response = requests.get(API_ENDPOINT, headers=headers, params=params)
        response.raise_for_status() # Lanza una excepción para errores HTTP 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error al contactar la API: {str(e)}"}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}

schema = {
    "name": "obtener_datos_servicio",
    "description": "Consulta un servicio externo para obtener datos específicos basados en un parámetro de búsqueda. Requiere configuración de API Key.",
    "postprocess": True,
    "parameters": {
        "type": "object",
        "properties": {
            "parametro_busqueda": {
                "type": "string",
                "description": "El término o consulta para buscar en el servicio externo."
            }
        },
        "required": ["parametro_busqueda"]
    }
}
```
HALion también tiene una utilidad para detectar variables de entorno (`env_detection.py`) y un gestor (`env_manager.py`) que se utilizan al generar tools con IA, pero para el desarrollo manual, `dotenv` es el enfoque directo.

## 7. Ejemplos de Herramientas

### Ejemplo 1: Herramienta Simple (`saludar`)

Este es un ejemplo básico, similar al `main_context.md`.

```python
# app/tools/saludar.py

def saludar(nombre: str, formal: bool = False) -> str:
    """
    Genera un saludo personalizado según el nombre y la formalidad.

    Args:
        nombre (str): Nombre de la persona a saludar.
        formal (bool, optional): Si el saludo debe ser formal. Por defecto es False.

    Returns:
        str: Saludo generado.
    """
    if formal:
        return f"Estimado/a {nombre}, es un placer saludarle."
    return f"¡Hola {nombre}! ¿Cómo estás?"

schema = {
  "name": "saludar",
  "description": "Genera un saludo personalizado. Puede ser formal o informal.",
  "postprocess": True,
  "parameters": {
    "type": "object",
    "properties": {
      "nombre": {
        "type": "string",
        "description": "El nombre de la persona a la que se dirigirá el saludo."
      },
      "formal": {
        "type": "boolean",
        "description": "Especifica si el saludo debe ser formal (true) o informal (false)."
      }
    },
    "required": ["nombre"]
  }
}
```

### Ejemplo 2: Herramienta Avanzada (`obtener_clima`)

Esta herramienta simula obtener el clima de una ciudad usando una (falsa) API.

```python
# app/tools/obtener_clima.py
import os
from dotenv import load_dotenv
import random # Para simular respuestas de API

# Cargar variables de entorno
load_dotenv()

CLIMA_API_KEY = os.getenv("CLIMA_API_KEY") # Simular que necesitamos una API key

def obtener_clima(ciudad: str) -> dict:
    """
    Obtiene el pronóstico del clima para una ciudad específica.
    Simula una llamada a una API de clima.

    Args:
        ciudad (str): El nombre de la ciudad para la cual obtener el clima.

    Returns:
        dict: Un diccionario con la información del clima o un error.
    """
    if not CLIMA_API_KEY:
        # En una tool real, podrías querer que esto sea un error que detenga la ejecución
        # o simplemente un aviso, dependiendo de la criticidad de la API key.
        print("Advertencia: CLIMA_API_KEY no está configurada. Usando datos simulados.")
        # return {"error": "CLIMA_API_KEY no configurada. Verifica tus variables de entorno."}


    # Simulación de llamada a API
    try:
        # Aquí iría la lógica real para llamar a una API de clima
        # import requests
        # response = requests.get(f"https://api.climatiempo.com/v1/forecast?city={ciudad}&apikey={CLIMA_API_KEY}")
        # response.raise_for_status()
        # data = response.json()

        # Datos simulados para el ejemplo:
        temperaturas = ["soleado", "nublado", "lluvioso", "tormenta eléctrica", "nieve ligera"]
        data = {
            "ciudad": ciudad,
            "temperatura_celsius": random.randint(-5, 35),
            "descripcion": random.choice(temperaturas),
            "humedad_porcentaje": random.randint(30, 90),
            "viento_kmh": random.randint(0, 25)
        }
        return data
    except Exception as e:
        # Captura errores genéricos o específicos de la librería de requests
        return {"error": f"No se pudo obtener el clima para {ciudad}: {str(e)}"}

schema = {
  "name": "obtener_clima",
  "description": "Proporciona el pronóstico del tiempo actual para una ciudad dada. Puede incluir temperatura, descripción, humedad y viento.",
  "postprocess": False, # El resultado es directo y estructurado, el LLM no necesita re-procesarlo mucho.
  "parameters": {
    "type": "object",
    "properties": {
      "ciudad": {
        "type": "string",
        "description": "El nombre de la ciudad para la cual se desea el pronóstico del tiempo (ej: 'Madrid', 'Buenos Aires')."
      }
    },
    "required": ["ciudad"]
  }
}
```

## 8. Registro y Activación de Herramientas

*   **Carga Automática:** HALion (`ToolManager` y `ToolDefinitionRegistry`) escanea el directorio `app/tools/` al iniciarse. Si tu archivo `.py` y su `schema` están correctamente definidos y ubicados, tu herramienta debería cargarse automáticamente.
*   **Panel de Administración:**
    *   Una vez cargada, tu herramienta aparecerá en el panel de administración de HALion (`Tools View`).
    *   Desde allí, puedes:
        *   **Activar o Desactivar** la herramienta para que el LLM la considere o no.
        *   Configurar el comportamiento de **Post-procesado** (`postprocess`) individualmente.
        *   Ver el código y el schema.
*   **Errores de Carga:** Si hay problemas al cargar tu herramienta (ej: sintaxis incorrecta, schema malformado, nombres no coincidentes), HALion registrará un error. Revisa los logs de la consola o los logs de depuración (`debug_logs/file_creation_debug.log`) para más detalles.

## 9. Buenas Prácticas de Desarrollo

*   **Atomicidad:** Diseña herramientas que realicen una tarea específica y bien definida. Evita herramientas monolíticas que intenten hacer demasiadas cosas.
*   **Descripciones Claras (para el LLM):** La calidad de las descripciones en tu `schema` (tanto de la herramienta como de sus parámetros) es crucial. El LLM se basa en ellas. Sé preciso, conciso y proporciona ejemplos si es necesario en la descripción.
*   **Manejo Robusto de Errores:** Anticipa posibles fallos (entradas incorrectas, servicios externos no disponibles, etc.) y maneja las excepciones de forma elegante. Devuelve mensajes de error útiles.
*   **Seguridad de Variables de Entorno:** Nunca incluyas API keys o secretos directamente en el código. Usa siempre variables de entorno y el archivo `.env`.
*   **Tipado Estricto:** Usa type hints de Python para todos los argumentos y valores de retorno. Ayuda a la claridad y a la detección temprana de errores.
*   **Comentarios en el Código:** Comenta las partes complejas de tu lógica para facilitar el mantenimiento.
*   **Idempotencia (cuando sea posible):** Si una herramienta se llama varias veces con los mismos parámetros, idealmente debería producir el mismo resultado sin efectos secundarios no deseados.
*   **Pruebas:** Aunque HALion no imponga un framework de pruebas, es altamente recomendable que pruebes tus herramientas individualmente para asegurar que funcionan como esperas antes de integrarlas.

## 10. Generación de Herramientas con IA

HALion incluye una funcionalidad para generar herramientas mediante IA. Puedes describir la herramienta que necesitas, y HALion intentará generar el código Python y el `schema` JSON.

*   Esto puede ser un excelente punto de partida.
*   **Siempre revisa y refina el código generado.** La IA puede cometer errores o no seguir todas las buenas prácticas.
*   Asegúrate de que el `schema` generado sea preciso y las descripciones sean óptimas para el LLM.

## 11. Solución de Problemas Comunes

*   **Herramienta no aparece en la UI:**
    *   Verifica la ubicación del archivo (debe estar en `app/tools/`).
    *   Comprueba las convenciones de nomenclatura (nombre de archivo == nombre de función == `schema["name"]`).
    *   Busca errores de sintaxis en tu archivo Python.
    *   Revisa los logs de HALion al inicio por mensajes de error durante la carga.
*   **LLM no usa la herramienta o la usa incorrectamente:**
    *   Mejora la `description` en el `schema` de la herramienta y sus parámetros. Hazla más clara, más específica o añade ejemplos de cuándo usarla.
    *   Asegúrate de que los `type` en `properties` del schema son correctos.
    *   Verifica que la herramienta esté activada en el panel de administración.
*   **Errores de `TypeError` o `ValueError` al ejecutar la herramienta:**
    *   El LLM podría estar pasando parámetros con tipos incorrectos o valores inválidos. Añade validación más robusta dentro de tu función Python o mejora las descripciones de los parámetros en el schema para guiar mejor al LLM.
*   **Problemas con Variables de Entorno:**
    *   Asegúrate de que `load_dotenv()` se llama (si usas ese método).
    *   Verifica que las variables están correctamente definidas en tu archivo `.env`.
    *   Comprueba que los nombres de las variables en `os.getenv("MI_VARIABLE")` coinciden exactamente con los del archivo `.env`.

---

Esta guía debería proporcionarte una base sólida para desarrollar herramientas potentes y fiables para HALion. ¡Feliz desarrollo! 