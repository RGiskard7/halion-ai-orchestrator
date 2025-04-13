<p align='center'>  
 <img src='docs/assets/github-banner.png' style="max-width: 100%; max-height: 180px; width: auto;"/>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-1.44+-red.svg" alt="Streamlit"></a>
  <a href="https://openai.com/blog/openai-api/"><img src="https://img.shields.io/badge/OpenAI-API-green.svg" alt="OpenAI API"></a>
</p>

Un framework extensible para crear, gestionar y desplegar asistentes IA con capacidades personalizadas a través de herramientas modulares.

## 🌟 Características Principales

- **🤖 Chat con Modelos Avanzados**: Interactúa con modelos de OpenAI (GPT-4, GPT-3.5) con una interfaz intuitiva.
- **🔧 Herramientas Dinámicas**: Crea, gestiona y activa herramientas personalizadas para potenciar tu asistente IA.
- **🧩 Arquitectura Modular**: Amplía las capacidades de tu IA sin necesidad de modificar el código principal.
- **✨ Generación Asistida**: Permite a la IA crear nuevas herramientas mediante auto-programación.
- **📊 Panel de Administración**: Administra herramientas, configuraciones y capacidades del sistema desde una interfaz visual.
- **🔄 Integración Flexible**: Conecta con servicios externos, APIs y fuentes de datos a través de herramientas personalizadas.
- **📝 Contexto Persistente**: Mantiene el historial de conversación para proporcionar respuestas contextuales.
- **⚙️ Configuración de Modelos**: Personaliza parámetros como temperatura, max_tokens y otros ajustes del modelo.
- **🔌 Múltiples Protocolos**: Soporte para diferentes protocolos de comunicación con la IA (completions, chat).
- **📚 Documentación Integrada**: Documentación completa y ejemplos incluidos para facilitar el desarrollo.

## 🛠️ Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/openai-modular-mcp.git
   cd openai-modular-mcp
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configura tu clave API de OpenAI:
   - Crea un archivo `.env` en el directorio raíz
   - Añade tu clave API: `OPENAI_API_KEY=tu_clave_api`

## 🚀 Uso Rápido

Ejecuta la aplicación con:

```bash
python run.py
```

O alternativamente:

```bash
streamlit run app/main.py
```

Abre tu navegador en [http://localhost:8501](http://localhost:8501) para interactuar con la interfaz.

## 📋 Guía de Uso

### Interacción con el Asistente

1. Escribe tu mensaje en el área de texto y presiona "Enviar" o Enter.
2. El asistente responderá y podrá utilizar las herramientas disponibles si es necesario.
3. Las herramientas utilizadas y sus resultados se muestran dentro de la conversación.

### Gestión de Herramientas

1. Accede a la sección "Administración" para gestionar tus herramientas.
2. Para crear una nueva herramienta:
   - Define un nombre claro y descriptivo
   - Configura el schema JSON que define sus parámetros
   - Implementa el código Python que ejecutará la funcionalidad
   - Guarda y activa la herramienta

3. Para generar una nueva herramienta con ayuda de la IA:
   - Describe la funcionalidad deseada
   - Revisa y edita el código generado si es necesario
   - Confirma la creación

### Configuración del Sistema

Accede a la sección "Configuración" para ajustar:
- Modelo de OpenAI a utilizar
- Parámetros del modelo (temperatura, tokens máximos, etc.)
- Comportamiento general del sistema

## 🧰 Estructura del Proyecto

```
openai-modular-mcp/
├── app/                      # Código principal de la aplicación
│   ├── api/                  # Endpoints y servicios API
│   ├── components/           # Componentes de la interfaz Streamlit
│   ├── controllers/          # Lógica de controladores
│   ├── models/               # Modelos de datos
│   ├── tools/                # Herramientas dinámicas
│   ├── utils/                # Utilidades generales
│   └── main.py               # Punto de entrada de la aplicación
├── docs/                     # Documentación
├── tests/                    # Pruebas automatizadas
├── .env                      # Variables de entorno (creado por el usuario)
├── requirements.txt          # Dependencias del proyecto
└── run.py                    # Script de ejecución simplificado
```

## 🎯 Casos de Uso

- **Asistente Personal Aumentado**: Crea un asistente que pueda gestionar calendarios, correos y tareas.
- **Investigación de Datos**: Desarrolla herramientas para analizar conjuntos de datos y visualizar resultados.
- **Integración de Servicios**: Conecta tu asistente con servicios como Jira, GitHub, o Slack.
- **Automatización de Flujos de Trabajo**: Diseña flujos para tareas repetitivas con procesamiento inteligente.
- **Creación de Contenido**: Genera imágenes, textos o código con herramientas especializadas.

## 🔄 Actualización y Mejoras

El sistema está en constante evolución. Para actualizar a la última versión:

```bash
git pull origin main
pip install -r requirements.txt
```

Consulta el archivo [CHANGELOG.md](./CHANGELOG.md) para detalles sobre las actualizaciones.

## 🧩 Desarrollo de Herramientas

Las herramientas son el corazón del sistema MCP. Cada herramienta debe incluir:

1. **Nombre**: Identificador único y descriptivo
2. **Schema JSON**: Define los parámetros que acepta la herramienta
3. **Código de Implementación**: Lógica que ejecuta la funcionalidad

Ejemplo de una herramienta sencilla:

```python
def obtener_clima(ciudad: str) -> dict:
    """
    Obtiene información meteorológica para una ciudad
    
    Args:
        ciudad: Nombre de la ciudad
        
    Returns:
        dict: Datos meteorológicos
    """
    # Implementación de la lógica
    # ...
    return datos_clima
```

Consulta la [documentación de desarrollo](./docs/development.md) para más detalles sobre cómo crear herramientas complejas.

## 📚 Recursos Adicionales

- [Documentación Técnica](./main_context.md): Especificaciones técnicas y arquitectura.
- [Hoja de Ruta](./roadmap.md): Planes de desarrollo futuro.
- [Guía de Contribución](./CONTRIBUTING.md): Cómo contribuir al proyecto.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz fork del repositorio
2. Crea una rama para tu función (`git checkout -b feature/amazing-feature`)
3. Realiza tus cambios y haz commit (`git commit -m 'Add amazing feature'`)
4. Sube tus cambios (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](./LICENSE) para más detalles.

## 📞 Contacto

Si tienes preguntas, sugerencias o comentarios, no dudes en abrir un issue o contactar con el equipo de desarrollo.

---

<p align="center">
  <small>Desarrollado por <b>RGiskard7</b> ✨ con ❤️ por el poder de lo modular, lo limpio y lo hackeable</small>
</p> 