# HALion – Modular Intelligence Orchestrator

<p align='center'>  
 <img src='docs/assets/github-banner.png' style="max-width: 100%; max-height: 180px; width: auto;"/>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-1.44+-red.svg" alt="Streamlit"></a>
  <a href="https://openai.com/blog/openai-api/"><img src="https://img.shields.io/badge/OpenAI-API-green.svg" alt="OpenAI API"></a>
</p>

**HALion** es un framework extensible para crear, gestionar y desplegar asistentes IA con capacidades personalizadas a través de herramientas modulares, combinando potencia técnica con una experiencia de desarrollo fluida e intuitiva.

## 🌟 Características Principales

- **🤖 Chat con Modelos Avanzados**: Interfaz conversacional con soporte para GPT-4, GPT-3.5 y versiones Turbo.
- **🔧 Herramientas Dinámicas**: Añade nuevas capacidades fácilmente, gestionadas como plugins modulares.
- **🧩 Arquitectura Modular**: Cada herramienta es un bloque independiente que amplía el comportamiento del agente.
- **✨ Generación Automática de Tools**: Describe lo que quieres y la IA genera la herramienta por ti.
- **📊 Panel de Administración**: Todo el sistema bajo control desde una interfaz gráfica clara y personalizable.
- **🔄 Integración con APIs Externas**: Clima, búsqueda web, bases de datos y más.
- **⚙️ Configuración Avanzada de Modelos**: Ajustes detallados por modelo: temperatura, tokens, post-procesamiento.
- **📚 Documentación Integrada**: Guías, ejemplos y especificaciones directamente dentro del proyecto.

## 🛠️ Instalación

```bash
# Clona el proyecto
$ git clone https://github.com/tu-usuario/halion.git
$ cd halion

# Crea un entorno virtual
$ python -m venv venv
$ source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala las dependencias
$ pip install -r requirements.txt

# Configura tu API Key en el archivo .env
$ cp .env.example .env
# Edita el archivo y añade tu clave de OpenAI
```

## 🚀 Uso Rápido

```bash
python run.py
```

Abre tu navegador en [http://localhost:8501](http://localhost:8501).

## 🧭 Guía de Navegación

### 💬 Chat con Herramientas
- Escribe tu mensaje.
- Si es necesario, el asistente invocará automáticamente una herramienta.
- El resultado se integrará en la conversación o se mostrará directamente.

### ⚙️ Administración
- Crea herramientas nuevas desde cero o con ayuda de la IA.
- Activa/desactiva herramientas sin tocar código.
- Gestiona variables de entorno, configura parámetros de modelo.
- Visualiza y exporta logs de actividad.

### 🧠 Herramientas Generadas con IA
- Describe la funcionalidad deseada.
- HALion genera el código, valida la sintaxis y activa la herramienta automáticamente.
- Puedes editar el código antes de usarlo.

## 🧰 Estructura del Proyecto

```
openai-modular-mcp/
├── app/                      # Código principal de la aplicación
│   ├── components/           # Componentes de la interfaz Streamlit
│   ├── controllers/          # Lógica de controladores
│   ├── core/                 # Funcionalidades centrales
│   │   ├── dynamic_tool_registry.py  # Registro de herramientas dinámicas
│   │   ├── executor.py       # Orquestador de OpenAI
│   │   ├── logger.py         # Sistema de logs
│   │   └── tool_manager.py   # Gestión de herramientas
│   ├── debug_logs/           # Logs específicos de la aplicación
│   │   ├── file_creation_debug.log
│   │   └── tool_calls.log
│   ├── config/               # Configuraciones persistentes
│   │   └── .tool_status.json # Estado de activación de herramientas
│   ├── models/               # Modelos de datos
│   ├── tools/                # Herramientas disponibles
│   ├── utils/                # Utilidades generales
│   │   └── ai_generation.py  # Generación de herramientas con IA
│   ├── views/                # Vistas de la aplicación
│   │   ├── admin_view.py     # Panel de administración
│   │   ├── chat_view.py      # Interfaz de chat
│   │   └── tools_view.py     # Gestión de herramientas
│   └── main.py               # Punto de entrada de la aplicación
├── docs/                     # Documentación
│   ├── assets/               # Recursos visuales (imágenes, iconos)
│   └── images/               # Imágenes para documentación
├── .env                      # Variables de entorno (privado)
├── .env.example              # Plantilla de variables de entorno
├── requirements.txt          # Dependencias del proyecto
├── pyproject.toml            # Configuración del proyecto
├── run.py                    # Script de ejecución simplificado
├── main_context.md           # Arquitectura y contexto técnico
└── roadmap.md                # Plan de desarrollo
```

## 🎯 Casos de Uso

- **Agente Conversacional Empresarial**: Gestiona agendas, sistemas internos, y bases de datos.
- **Dashboards Inteligentes**: Interfaz conversacional para análisis de datos y reportes.
- **IA para Automatización**: Ejecuta flujos definidos por herramientas invocadas por IA.
- **Integración con Apps y APIs**: Llama APIs externas y procesa los resultados mediante tools personalizadas.
- **Desarrollo de Prototipos**: Diseña asistentes y flujos rápidamente sin backend complejo.

## 🔄 Mantenimiento y Mejora

```bash
git pull origin main
pip install -r requirements.txt
```

Consulta el [CHANGELOG.md](./CHANGELOG.md) para más detalles.

## 📚 Recursos Clave

- [📄 Arquitectura y contexto](./main_context.md)
- [🛠️ Guía de desarrollo de tools](./docs/development.md)
- [🧭 Roadmap](./roadmap.md)
- [🧬 Contribuciones](./CONTRIBUTING.md)

## 🤝 Cómo Contribuir

1. Haz fork del repositorio
2. Crea una rama para tu funcionalidad (`feature/nombre`)
3. Haz commit y push (`git commit -m 'Tu cambio'`)
4. Abre un Pull Request con tu mejora

## 📞 Contacto

Para sugerencias, errores o mejoras, abre un issue o contáctame directamente.

---

<p align="center">
  <small>Desarrollado por <b>RGiskard7</b> ⚡ impulsado por HALion – IA modular y orquestada.</small>
</p>

