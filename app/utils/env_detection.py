import re
from typing import List, Dict, Any

def detect_env_variables(code: str) -> List[Dict[str, Any]]:
    """
    Detecta posibles variables de entorno en el código generado.
    
    Args:
        code (str): Código Python a analizar
    
    Returns:
        list: Lista de diccionarios con información de las variables de entorno encontradas
    """
    # Patrones para buscar variables de entorno
    patterns = [
        # Patrones estándar de dotenv/os
        r'os\.environ\.get\(["\']([A-Za-z0-9_]+)["\']',              # os.environ.get('VAR_NAME')
        r'os\.getenv\(["\']([A-Za-z0-9_]+)["\']',                    # os.getenv('VAR_NAME')
        r'os\.environ\[["\']([A-Za-z0-9_]+)["\']\]',                 # os.environ['VAR_NAME']
        r'environ\.get\(["\']([A-Za-z0-9_]+)["\']',                  # environ.get('VAR_NAME')
        r'environ\[["\']([A-Za-z0-9_]+)["\']\]',                     # environ['VAR_NAME']
        r'getenv\(["\']([A-Za-z0-9_]+)["\']',                        # getenv('VAR_NAME')
        r'load_dotenv.*?\n.*?["\']([A-Za-z0-9_]+)["\']',             # Después de load_dotenv()
        
        # Patrones para variables hardcoded (claves API, etc)
        r'[\'"]([A-Za-z0-9_]+_(?:KEY|TOKEN|SECRET|API|AUTH|PASSWORD|PASS|PWD|APIKEY|APISECRET|ID))[\'"]',    # Variables con prefijo/sufijo de clave
        r'[\'"]([A-Za-z0-9]{32,})[\'"]',                              # Cadenas largas que parecen claves
        r'[\'"]([a-zA-Z0-9]{5,}\.[a-zA-Z0-9]{5,}\.[a-zA-Z0-9-_]{5,})[\'"]',  # Cadenas con formato de JWT/token
        
        # Strings literales que parecen URLs de API con claves
        r'[\'"]https?://[^\'"]+[\?&](?:key|token|api_key|apikey|auth)=([^&\'"]+)[\'"]',  # URLs con parámetros api_key
        r'[\'"]https?://[^\'"]+/auth/[^/\'"]+/([^/\'"]+)[\'"]',      # URLs con componentes de autenticación
        
        # Buscar constantes que parecen ser credenciales
        r'(?:API_KEY|TOKEN|AUTH_TOKEN|SECRET|PASSWORD)\s*=\s*[\'"]([^\'"]+)[\'"]',  # CONST = "valor"
        
        # Detección de asignación a variables que parecen claves
        r'([A-Za-z0-9_]+(?:key|token|secret|api|auth|password|apikey))(?:\s*=\s*)[\'"][^\'"]{5,}[\'"]',  # var_name = "valor"
    ]
    
    env_vars = []
    var_names_found = set()  # Para evitar duplicados
    
    # Buscar ocurrencias de estos patrones
    for pattern in patterns:
        matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            # Extraer nombre de variable según el patrón
            var_name = None
            
            # Si es un patrón de os.environ o similar, el grupo 1 es el nombre de variable
            var_name = match.group(1)
            
            # Verificar que tenemos un nombre de variable y no es un valor literal o URL
            if var_name and not var_name.startswith(('http', 'https', '{')):
                # Normalizar nombres de variables que puedan ser valores
                if len(var_name) > 30 or re.match(r'^[A-Za-z0-9+/=]+$', var_name):
                    # Esto parece un valor no un nombre, intentamos extraer un nombre del contexto
                    context_start = max(0, match.start() - 100)
                    context = code[context_start:match.start()]
                    name_match = re.search(r'([A-Z0-9_]+)\s*=\s*[\'"]', context)
                    if name_match:
                        var_name = name_match.group(1)
                    else:
                        # Si no podemos encontrar un nombre, usamos un nombre genérico
                        var_name = f"API_KEY_{len(var_names_found) + 1}"
            
                # Verificar que es un nombre válido de variable y no está duplicado
                if var_name and var_name not in var_names_found and len(var_name) > 2:
                    var_names_found.add(var_name)
                    
                    # Intentar detectar una descripción en el contexto
                    context_lines = code[max(0, match.start() - 200):match.start()].split('\n')
                    description = ""
                    
                    # Buscar en comentarios o docstrings cerca
                    for line in reversed(context_lines):
                        line = line.strip()
                        if "#" in line:
                            desc_part = line.split("#", 1)[1].strip()
                            if len(desc_part) > 5:  # Solo si parece una descripción real
                                description = desc_part
                                break
                        if '"""' in line or "'''" in line:
                            desc_part = line.replace('"""', '').replace("'''", '').strip()
                            if len(desc_part) > 5:
                                description = desc_part
                                break
                    
                    if not description:
                        # Generar descripción basada en el nombre
                        var_name_readable = var_name.replace('_', ' ').lower()
                        description = f"Variable de entorno para {var_name_readable}"
                    
                    # Determinar el tipo de variable
                    var_type = "API_KEY"  # Por defecto
                    var_name_upper = var_name.upper()
                    if "TOKEN" in var_name_upper:
                        var_type = "TOKEN"
                    elif "SECRET" in var_name_upper:
                        var_type = "SECRET"
                    elif "PASSWORD" in var_name_upper or "PASS" in var_name_upper or "PWD" in var_name_upper:
                        var_type = "PASSWORD"
                    elif "URL" in var_name_upper or "ENDPOINT" in var_name_upper:
                        var_type = "URL"
                    elif "ID" in var_name_upper and not any(x in var_name_upper for x in ["KEY", "TOKEN", "SECRET"]):
                        var_type = "ID"
                    
                    env_vars.append({
                        "name": var_name,
                        "description": description,
                        "value": "",
                        "type": var_type
                    })
    
    return env_vars 