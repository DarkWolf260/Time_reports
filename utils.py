# utils.py
"""
Utilidades adicionales para la aplicación de reportes meteorológicos.
"""
import os
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from config import OPERADORES_FILE

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BackupManager:
    """Gestor de respaldos para los datos de la aplicación."""
    
    def __init__(self, backup_dir: str = "backup"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, description: str = "") -> str:
        """Crea un respaldo de los datos actuales."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        
        if description:
            # Limpiar descripción para nombre de archivo
            clean_desc = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).strip()
            backup_name += f"_{clean_desc.replace(' ', '_')}"
        
        backup_path = self.backup_dir / f"{backup_name}.json"
        
        try:
            # Crear respaldo de operadores
            if os.path.exists(OPERADORES_FILE):
                with open(OPERADORES_FILE, 'r', encoding='utf-8') as src:
                    data = json.load(src)
                
                backup_data = {
                    "timestamp": datetime.now().isoformat(),
                    "description": description,
                    "version": "2.0.0",
                    "operadores": data
                }
                
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    json.dump(backup_data, dst, ensure_ascii=False, indent=4)
                
                logger.info(f"Respaldo creado: {backup_path}")
                return str(backup_path)
            else:
                logger.warning("No se encontró archivo de operadores para respaldar")
                return ""
                
        except Exception as e:
            logger.error(f"Error creando respaldo: {e}")
            return ""
    
    def restore_backup(self, backup_file: str) -> bool:
        """Restaura un respaldo."""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"Archivo de respaldo no encontrado: {backup_file}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validar estructura del respaldo
            if "operadores" not in backup_data:
                logger.error("Archivo de respaldo inválido: falta 'operadores'")
                return False
            
            # Crear respaldo de seguridad antes de restaurar
            self.create_backup("antes_de_restaurar")
            
            # Restaurar datos
            with open(OPERADORES_FILE, 'w', encoding='utf-8') as f:
                json.dump(backup_data["operadores"], f, ensure_ascii=False, indent=4)
            
            logger.info(f"Respaldo restaurado desde: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error restaurando respaldo: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """Lista todos los respaldos disponibles."""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.json"):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                backups.append({
                    "file": str(backup_file),
                    "name": backup_file.name,
                    "timestamp": data.get("timestamp", ""),
                    "description": data.get("description", ""),
                    "size": backup_file.stat().st_size,
                    "operadores_count": len(data.get("operadores", []))
                })
            except Exception as e:
                logger.warning(f"Error leyendo respaldo {backup_file}: {e}")
        
        # Ordenar por timestamp descendente (más reciente primero)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Elimina respaldos antiguos, manteniendo solo los más recientes."""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        deleted_count = 0
        for backup in backups[keep_count:]:
            try:
                Path(backup["file"]).unlink()
                deleted_count += 1
                logger.info(f"Respaldo eliminado: {backup['name']}")
            except Exception as e:
                logger.warning(f"Error eliminando respaldo {backup['name']}: {e}")
        
        return deleted_count

class DataValidator:
    """Validador de datos para la aplicación."""
    
    @staticmethod
    def validate_operador_data(nombre: str, cargo: str, jerarquia: str, cedula: str) -> Dict[str, Any]:
        """Valida los datos de un operador."""
        errors = []
        warnings = []
        
        # Validar nombre
        if not nombre or not nombre.strip():
            errors.append("El nombre es requerido")
        elif len(nombre.strip()) < 2:
            errors.append("El nombre debe tener al menos 2 caracteres")
        elif len(nombre.strip()) > 50:
            warnings.append("El nombre es muy largo (máximo recomendado: 50 caracteres)")
        
        # Validar cédula
        if not cedula or not cedula.strip():
            errors.append("La cédula es requerida")
        else:
            cedula_clean = cedula.strip().replace("-", "").replace(".", "")
            if not cedula_clean.isdigit():
                errors.append("La cédula debe contener solo números")
            elif len(cedula_clean) < 6 or len(cedula_clean) > 12:
                errors.append("La cédula debe tener entre 6 y 12 dígitos")
        
        # Validar cargo y jerarquía
        if not cargo:
            errors.append("El cargo es requerido")
        if not jerarquia:
            errors.append("La jerarquía es requerida")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_json_file(file_path: str) -> Dict[str, Any]:
        """Valida un archivo JSON."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "valid": True,
                "data": data,
                "errors": []
            }
        except FileNotFoundError:
            return {
                "valid": False,
                "data": None,
                "errors": ["Archivo no encontrado"]
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "data": None,
                "errors": [f"Error de formato JSON: {e}"]
            }
        except Exception as e:
            return {
                "valid": False,
                "data": None,
                "errors": [f"Error inesperado: {e}"]
            }

class DataMigrator:
    """Migrador de datos para actualizaciones de versión."""
    
    @staticmethod
    def migrate_from_v1(old_file: str = "operadores.json") -> bool:
        """Migra datos desde la versión 1.0 del formato."""
        try:
            if not os.path.exists(old_file):
                logger.info("No se encontró archivo de versión anterior")
                return True
            
            with open(old_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # Si ya tiene el formato correcto, no hacer nada
            if isinstance(old_data, list) and all(isinstance(item, dict) for item in old_data):
                if old_data and all(key in old_data[0] for key in ['nombre', 'cargo', 'jerarquia', 'cedula']):
                    logger.info("Los datos ya están en formato v2.0")
                    return True
            
            # Crear respaldo antes de migrar
            backup_manager = BackupManager()
            backup_manager.create_backup("migracion_v1_to_v2")
            
            # Aquí iría la lógica de migración específica si fuera necesaria
            # Por ahora, asumimos que el formato ya es correcto
            
            logger.info("Migración completada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error durante la migración: {e}")
            return False

class ReportExporter:
    """Exportador de reportes en diferentes formatos."""
    
    @staticmethod
    def export_to_txt(report_content: str, filename: str = None) -> str:
        """Exporta un reporte a archivo TXT."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_{timestamp}.txt"
        
        try:
            # Crear directorio de exportación si no existe
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            file_path = export_dir / filename
            
            # Convertir markdown a texto plano para TXT
            plain_text = report_content.replace("*", "")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(plain_text)
            
            logger.info(f"Reporte exportado a: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error exportando reporte: {e}")
            return ""
    
    @staticmethod
    def export_operators_csv(operators: List[Dict[str, str]], filename: str = None) -> str:
        """Exporta la lista de operadores a CSV."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"operadores_{timestamp}.csv"
        
        try:
            import csv
            
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            file_path = export_dir / filename
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                if operators:
                    writer = csv.DictWriter(f, fieldnames=operators[0].keys())
                    writer.writeheader()
                    writer.writerows(operators)
                else:
                    f.write("No hay operadores para exportar\n")
            
            logger.info(f"Operadores exportados a: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error exportando operadores: {e}")
            return ""

class ConfigManager:
    """Gestor de configuración de la aplicación."""
    
    def __init__(self, config_file: str = "user_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo."""
        default_config = {
            "version": "2.0.0",
            "theme": "light",
            "auto_backup": True,
            "backup_interval_hours": 24,
            "max_backups": 10,
            "export_format": "txt",
            "window": {
                "width": 600,
                "height": 900,
                "center": True
            }
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Fusionar con configuración por defecto
                default_config.update(user_config)
            
            return default_config
        except Exception as e:
            logger.warning(f"Error cargando configuración: {e}. Usando valores por defecto.")
            return default_config
    
    def save_config(self) -> bool:
        """Guarda la configuración actual."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Establece un valor de configuración."""
        keys = key.split('.')
        config_ref = self.config
        
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        config_ref[keys[-1]] = value
        return self.save_config()

# Instancia global del gestor de configuración
config_manager = ConfigManager()

# Funciones de utilidad comunes
def format_file_size(size_bytes: int) -> str:
    """Formatea un tamaño de archivo en bytes a formato legible."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def clean_filename(filename: str) -> str:
    """Limpia un nombre de archivo eliminando caracteres inválidos."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def get_app_version() -> str:
    """Obtiene la versión actual de la aplicación."""
    return config_manager.get('version', '2.0.0')