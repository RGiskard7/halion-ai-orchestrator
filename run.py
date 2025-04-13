# run.py
import os
import subprocess
import sys
import shutil

def check_dirs():
    """Verifica y crea los directorios necesarios si no existen"""
    # Obtener el directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Directorios importantes
    app_dir = os.path.join(current_dir, "app")
    tools_dir = os.path.join(app_dir, "tools")
    debug_logs_dir = os.path.join(app_dir, "debug_logs")
    config_dir = os.path.join(app_dir, "config")
    
    # Crear directorios si no existen
    for dir_path in [app_dir, tools_dir, debug_logs_dir, config_dir]:
        if not os.path.exists(dir_path):
            print(f"Creando directorio: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
    
    # Si hay herramientas en el directorio old_tools pero no en app/tools, copiarlas
    old_tools_dir = os.path.join(current_dir, "tools")
    if os.path.exists(old_tools_dir) and os.path.isdir(old_tools_dir):
        if not os.listdir(tools_dir) and os.listdir(old_tools_dir):
            print("Copiando herramientas del directorio antiguo al nuevo...")
            for item in os.listdir(old_tools_dir):
                if item.endswith(".py"):
                    src = os.path.join(old_tools_dir, item)
                    dst = os.path.join(tools_dir, item)
                    print(f"Copiando: {src} -> {dst}")
                    shutil.copy2(src, dst)
    
    # Migrar archivos de configuración y logs si están en la raíz
    # 1. Migrar .tool_status.json
    old_tool_status = os.path.join(current_dir, ".tool_status.json")
    new_tool_status = os.path.join(config_dir, ".tool_status.json")
    if os.path.exists(old_tool_status) and not os.path.exists(new_tool_status):
        print(f"Migrando .tool_status.json a {config_dir}...")
        shutil.copy2(old_tool_status, new_tool_status)
        os.remove(old_tool_status)
        print("✅ Migración completada y archivo original eliminado")
    
    # 2. Migrar tool_calls.log
    old_tool_calls = os.path.join(current_dir, "tool_calls.log")
    new_tool_calls = os.path.join(debug_logs_dir, "tool_calls.log")
    if os.path.exists(old_tool_calls) and not os.path.exists(new_tool_calls):
        print(f"Migrando tool_calls.log a {debug_logs_dir}...")
        shutil.copy2(old_tool_calls, new_tool_calls)
        os.remove(old_tool_calls)
        print("✅ Migración completada y archivo original eliminado")
    
    return current_dir

def run_streamlit():
    """Ejecuta la aplicación Streamlit"""
    try:
        # Verificar y crear directorios
        current_dir = check_dirs()
        
        # Establecer el directorio del proyecto como directorio de trabajo
        os.chdir(current_dir)
        
        # Comando para ejecutar Streamlit con más información de depuración
        cmd = [sys.executable, "-m", "streamlit", "run", "app/main.py", "--logger.level=info"]
        
        print("Ejecutando Streamlit con el siguiente comando:")
        print(" ".join(cmd))
        print(f"Directorio de trabajo: {os.getcwd()}")
        
        # Ejecutar el comando
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nAplicación terminada por el usuario. ¡Hasta pronto! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_streamlit() 