# setup.py
"""
Script de instalación y configuración para la aplicación de reportes meteorológicos.
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Muestra el banner de instalación."""
    print("=" * 60)
    print("  INSTALACIÓN - REPORTES METEOROLÓGICOS")
    print("  Protección Civil Municipio Guanta")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    print("🔍 Verificando versión de Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_dependencies():
    """Instala las dependencias del proyecto."""
    print("\n📦 Instalando dependencias...")
    
    try:
        # Actualizar pip
        print("   Actualizando pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Instalar requirements
        if os.path.exists("requirements.txt"):
            print("   Instalando desde requirements.txt...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("   Instalando Flet directamente...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flet>=0.24.0"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ Dependencias instaladas correctamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def create_directory_structure():
    """Crea la estructura de directorios necesaria."""
    print("\n📁 Configurando estructura de directorios...")
    
    directories = [
        "data",      # Para archivos de datos
        "logs",      # Para archivos de log
        "backup"     # Para respaldos
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ Directorio '{directory}' creado/verificado")

def create_initial_config():
    """Crea la configuración inicial si no existe."""
    print("\n⚙️  Configurando archivos iniciales...")
    
    # Crear archivo de operadores vacío si no existe
    operadores_file = "operadores.json"
    if not os.path.exists(operadores_file):
        with open(operadores_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        print(f"   ✅ Archivo '{operadores_file}' creado")
    else:
        print(f"   ✅ Archivo '{operadores_file}' ya existe")
    
    # Crear archivo de configuración de usuario
    user_config = {
        "version": "2.0.0",
        "first_run": True,
        "default_theme": "light",
        "window_position": {
            "center": True
        }
    }
    
    config_file = "user_config.json"
    if not os.path.exists(config_file):
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(user_config, f, ensure_ascii=False, indent=4)
        print(f"   ✅ Archivo '{config_file}' creado")

def verify_installation():
    """Verifica que la instalación sea correcta."""
    print("\n🔎 Verificando instalación...")
    
    try:
        import flet
        print(f"   ✅ Flet {flet.__version__} importado correctamente")
    except ImportError:
        print("   ❌ Error: No se puede importar Flet")
        return False
    
    # Verificar archivos principales
    required_files = [
        "main.py",
        "config.py", 
        "models.py",
        "styles.py",
        "ui_components.py"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - FALTA")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Faltan archivos: {', '.join(missing_files)}")
        return False
    
    return True

def create_shortcuts():
    """Crea accesos directos (solo en Windows)."""
    if sys.platform == "win32":
        print("\n🔗 Creando accesos directos...")
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Reportes Meteorológicos.lnk")
            target = os.path.join(os.getcwd(), "main.py")
            wDir = os.getcwd()
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print("   ✅ Acceso directo creado en el escritorio")
        except ImportError:
            print("   ⚠️  No se pudo crear acceso directo (falta winshell)")
        except Exception as e:
            print(f"   ⚠️  No se pudo crear acceso directo: {e}")

def run_tests():
    """Ejecuta pruebas básicas si están disponibles."""
    if os.path.exists("test_models.py"):
        print("\n🧪 Ejecutando pruebas...")
        try:
            result = subprocess.run([sys.executable, "-m", "unittest", "test_models", "-v"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("   ✅ Todas las pruebas pasaron")
            else:
                print("   ⚠️  Algunas pruebas fallaron, pero la instalación puede continuar")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            print(f"   ⚠️  Error ejecutando pruebas: {e}")

def main():
    """Función principal de instalación."""
    print_banner()
    
    # Verificar requisitos
    if not check_python_version():
        return 1
    
    # Instalar dependencias
    if not install_dependencies():
        return 1
    
    # Configurar proyecto
    create_directory_structure()
    create_initial_config()
    
    # Verificar instalación
    if not verify_installation():
        return 1
    
    # Extras opcionales
    create_shortcuts()
    run_tests()
    
    # Mensaje final
    print("\n" + "=" * 60)
    print("🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
    print("\nPara ejecutar la aplicación:")
    print("   python main.py")
    print("\nPara ejecutar pruebas:")
    print("   python -m pytest test_models.py -v")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())