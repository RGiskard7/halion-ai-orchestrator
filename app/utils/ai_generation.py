import openai
import re
import os

def generate_tool_with_ai(description: str, api_key: str, model: str = "gpt-4", temperature: float = 0.7) -> str:
    """
    Genera código para una herramienta usando la API de OpenAI.
    
    Args:
        description: Descripción de la herramienta a generar
        api_key: API key de OpenAI
        model: Modelo a utilizar (por defecto "gpt-4")
        temperature: Temperatura para la generación (por defecto 0.7)
        
    Returns:
        str: Código Python de la herramienta generada
    
    Raises:
        ValueError: Si hay algún error en la generación
    """
    try:                
        # Verificar que tenemos una API key válida
        if not api_key:
            raise ValueError("No se proporcionó una API key válida")
            
        # Configurar cliente OpenAI
        client = openai.OpenAI(api_key=api_key)
        
        # Prompt simplificado para funciones/tools de OpenAI
        prompt = f"""
        Crea una herramienta Python con función y schema compatible con GPT (function calling). No des explicaciones, solo el código entre triple comillas.

            TAREA: Crear una herramienta Python para GPT function calling que cumpla con la siguiente descripción:
            {description}

            1. ESTRUCTURA OBLIGATORIA:
                - Función principal con nombre descriptivo en snake_case
                - Docstring detallado
                - Tipado de parámetros y retorno
                - Schema JSON que define la herramienta
                - Manejo de errores apropiado

            2. SCHEMA JSON REQUERIDO:
                - name: Nombre de la función (debe coincidir)
                - description: Descripción clara y concisa
                - postprocess: boolean (si el resultado necesita procesamiento por IA)
                - parameters: Definición JSON Schema de parámetros
                - required: Lista de parámetros obligatorios

            3. GESTIÓN DE CREDENCIALES Y VARIABLES DE ENTORNO (MUY IMPORTANTE):
                - SIEMPRE usa os.getenv() o os.environ.get() para acceder a credenciales/tokens/claves
                - NUNCA incluyas credenciales directamente en el código
                - Usa nombres de variables descriptivos con sufijos _API_KEY, _TOKEN, etc.
                - Cada API key o credencial DEBE usar su propia variable de entorno
                - Incluye comentarios explicando qué es cada variable de entorno
                - Al inicio del archivo incluye 'from dotenv import load_dotenv' y 'load_dotenv()'
                - Verifica siempre si las variables están disponibles y maneja los casos de error

            4. BUENAS PRÁCTICAS:
                - Código limpio y comentado
                - Validaciones de entrada
                - Mensajes de error descriptivos
                - Retorno de datos estructurados

            FORMATO:
            ```python
            from typing import Dict, Optional, Union
            import requests
            import os
            from dotenv import load_dotenv

            # Cargar variables de entorno
            load_dotenv()

            def nombre_herramienta(param1: str, param2: Optional[int] = None) -> Dict[str, Union[str, int]]:
                \"\"\"
                Descripción detallada de la herramienta.
                
                Args:
                    param1 (str): Descripción del primer parámetro
                    param2 (int, optional): Descripción del segundo parámetro. Defaults to None.
                
                Returns:
                    Dict[str, Union[str, int]]: Descripción del formato de retorno
                    
                Raises:
                    ValueError: Descripción de cuándo se lanza este error
                \"\"\"
                # Obtener API key desde variables de entorno
                api_key = os.getenv("SERVICIO_API_KEY")
                if not api_key:
                    raise ValueError("API key no configurada. Añade SERVICIO_API_KEY a las variables de entorno.")
                
                # Validaciones
                if not param1:
                    raise ValueError("param1 no puede estar vacío")
                
                try:
                    # Lógica principal aquí
                    # ...
                    return resultado
                except Exception as e:
                    raise Exception(f"Error en nombre_herramienta: {{e}}")

            schema = {{
                "name": "nombre_herramienta",
                "description": "Descripción concisa de la funcionalidad",
                "postprocess": true, # Siempre true por defecto
                "parameters": {{
                    "type": "object",
                    "properties": {{
                        "param1": {{
                            "type": "string",
                            "description": "Descripción detallada del parámetro"
                        }},
                        "param2": {{
                            "type": "integer",
                            "description": "Descripción detallada del parámetro opcional"
                        }}
                    }},
                    "required": ["param1"]
                }}
            }}
            ```
            IMPORTANTE:
            - La herramienta debe ser funcional y segura
            - Debe ser compatible con las tools (antes function calling) de OpenAI
            - SIEMPRE usa variables de entorno para APIs, tokens, o cualquier credencial
        """
        
        # Llamada a la API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto desarrollador de herramientas para GPT function calling."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        # Obtener el contenido de la respuesta
        content = response.choices[0].message.content
        if not content:
            raise ValueError("La respuesta no contiene contenido")
            
        # Extraer el código Python
        code_match = re.search(r"```python(.*?)```", content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Si no encuentra bloques específicos de Python, buscar cualquier bloque de código
        code_blocks = re.findall(r'```(.*?)```', content, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        
        # Si no hay bloques de código, usar todo el contenido
        return content.strip()
        
    except Exception as e:
        raise ValueError(f"Error al generar código: {str(e)}") 