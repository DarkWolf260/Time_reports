# models.py
"""
Modelos de datos y lógica de negocio de la aplicación.
"""
import json
import os
import datetime
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from config import TIEMPO, EMOJI_TIEMPO, DEPARTAMENTO
import uuid

@dataclass
class Alarm:
    """Modelo para representar una alarma."""
    time: str  # Formato "HH:MM"
    alarm_type: str  # "sound" o "notification"
    active: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "time": self.time,
            "type": self.alarm_type,
            "active": self.active
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Alarm':
        # Compatibilidad con formato antiguo
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            time=data["time"],
            alarm_type=data.get("type", "sound"), # 'type' es el nuevo nombre
            active=data.get("active", True)
        )

@dataclass
class Operador:
    """Modelo para representar un operador."""
    nombre: str
    cargo: str
    jerarquia: str
    cedula: str
    
    def __str__(self) -> str:
        return f"{self.cargo} {self.jerarquia} {self.nombre} {self.cedula}"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "nombre": self.nombre,
            "cargo": self.cargo,
            "jerarquia": self.jerarquia,
            "cedula": self.cedula
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Operador':
        return cls(**data)

class OperadorManager:
    """Gestor para manejar operadores."""
    
    def __init__(self, page=None):
        self.page = page
        self._operadores: List[Operador] = []
        self.cargar_operadores()

    def cargar_operadores(self) -> None:
        """Carga los operadores desde el almacenamiento del cliente."""
        if self.page and self.page.client_storage:
            try:
                data_str = self.page.client_storage.get("operators")
                if data_str:
                    data = json.loads(data_str)
                    self._operadores = [Operador.from_dict(op) for op in data]
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error cargando operadores desde client_storage: {e}")
                self._operadores = []

    def guardar_operadores(self) -> None:
        """Guarda los operadores en el almacenamiento del cliente."""
        if self.page and self.page.client_storage:
            try:
                data = [op.to_dict() for op in self._operadores]
                self.page.client_storage.set("operators", json.dumps(data))
            except Exception as e:
                print(f"Error guardando operadores en client_storage: {e}")
    
    def agregar_operador(self, nombre: str, cargo: str, jerarquia: str, cedula: str) -> bool:
        """Agrega un nuevo operador."""
        if not all([nombre.strip(), cargo, jerarquia, cedula.strip()]):
            return False
        
        # Verificar si ya existe un operador con el mismo nombre o cédula
        if self.buscar_por_nombre(nombre.strip()) or self.buscar_por_cedula(cedula.strip()):
            return False
        
        operador = Operador(nombre.strip(), cargo, jerarquia, cedula.strip())
        self._operadores.append(operador)
        self.guardar_operadores()
        return True
    
    def eliminar_operador(self, nombre: str) -> bool:
        """Elimina un operador por nombre."""
        operador = self.buscar_por_nombre(nombre)
        if operador:
            self._operadores.remove(operador)
            self.guardar_operadores()
            return True
        return False
    
    def buscar_por_nombre(self, nombre: str) -> Optional[Operador]:
        """Busca un operador por nombre."""
        for op in self._operadores:
            if op.nombre == nombre:
                return op
        return None
    
    def buscar_por_cedula(self, cedula: str) -> Optional[Operador]:
        """Busca un operador por cédula."""
        for op in self._operadores:
            if op.cedula == cedula:
                return op
        return None
    
    def obtener_nombres(self) -> List[str]:
        """Obtiene la lista de nombres de operadores."""
        return [op.nombre for op in self._operadores]
    
    def obtener_operadores(self) -> List[Operador]:
        """Obtiene la lista completa de operadores."""
        return self._operadores.copy()
    
    def obtener_operador_por_indice(self, indice: int) -> Optional[Operador]:
        """Obtiene un operador por índice."""
        if 0 <= indice < len(self._operadores):
            return self._operadores[indice]
        return None
    
    def obtener_indice_por_nombre(self, nombre: str) -> int:
        """Obtiene el índice de un operador por nombre."""
        for i, op in enumerate(self._operadores):
            if op.nombre == nombre:
                return i
        return -1
    
    @property
    def cantidad(self) -> int:
        """Obtiene la cantidad de operadores."""
        return len(self._operadores)

class AlarmManager:
    """Gestor para manejar las alarmas, usando un archivo JSON para persistencia."""

    def __init__(self):
        self._alarms: List[Alarm] = []
        self._storage_path = self._get_storage_path()
        self.cargar_alarmas()

    def _get_storage_path(self) -> str:
        """Obtiene la ruta del archivo de almacenamiento de alarmas."""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            if context:
                return os.path.join(context.getFilesDir().getAbsolutePath(), 'alarms.json')
        except ImportError:
            pass # No estamos en Android, usar ruta local

        # Para desarrollo en escritorio
        return 'alarms.json'

    def cargar_alarmas(self) -> None:
        """Carga las alarmas desde el archivo JSON."""
        if not os.path.exists(self._storage_path):
            self._alarms = []
            return
        try:
            with open(self._storage_path, 'r') as f:
                data = json.load(f)
                self._alarms = [Alarm.from_dict(a) for a in data]
        except (json.JSONDecodeError, KeyError, TypeError, IOError) as e:
            print(f"Error cargando alarmas desde {self._storage_path}: {e}")
            self._alarms = []

    def guardar_alarmas(self) -> None:
        """Guarda las alarmas en el archivo JSON."""
        try:
            with open(self._storage_path, 'w') as f:
                data = [a.to_dict() for a in self._alarms]
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error guardando alarmas en {self._storage_path}: {e}")

    def agregar_alarma(self, time: str, alarm_type: str) -> Optional[Alarm]:
        """Agrega una nueva alarma."""
        if not time or not alarm_type:
            return None

        # Evitar duplicados exactos (misma hora y tipo)
        if any(a.time == time and a.alarm_type == alarm_type for a in self._alarms):
            return None

        new_alarm = Alarm(time=time, alarm_type=alarm_type)
        self._alarms.append(new_alarm)
        self.guardar_alarmas()
        return new_alarm

    def eliminar_alarma(self, alarm_id: str) -> bool:
        """Elimina una alarma por su ID."""
        alarm_a_eliminar = self.buscar_por_id(alarm_id)
        if alarm_a_eliminar:
            self._alarms.remove(alarm_a_eliminar)
            self.guardar_alarmas()
            return True
        return False

    def buscar_por_id(self, alarm_id: str) -> Optional[Alarm]:
        """Busca una alarma por su ID."""
        for alarm in self._alarms:
            if alarm.id == alarm_id:
                return alarm
        return None

    def obtener_alarmas(self) -> List[Alarm]:
        """Obtiene una copia de la lista de alarmas."""
        return self._alarms.copy()

class ReportGenerator:
    """Generador de reportes meteorológicos."""
    
    @staticmethod
    def generar_reporte(
        indice_tiempo: int,
        operador: Optional[Operador],
        municipio: str,
        departamento: str
    ) -> str:
        """Genera el reporte meteorológico."""
        fecha_actual = datetime.date.today().strftime('%d/%m/%Y')
        hora_actual = datetime.datetime.now().strftime('%H:%M')
        
        # Validar índice de tiempo
        if not (0 <= indice_tiempo < len(TIEMPO)):
            indice_tiempo = 0
        
        # Formatear operador
        operador_str = str(operador) if operador else "(Sin operador)"
        
        # Generar reporte
        reporte = (
            f"*PROTECCIÓN CIVIL MUNICIPIO {municipio.upper()}* 🚨\n\n"
            f"*·   REPORTE DEL ESTADO DEL TIEMPO:* {EMOJI_TIEMPO[indice_tiempo]}\n"
            f"*·   FECHA:* {fecha_actual}\n"
            f"*·   HORA:* {hora_actual} HLV\n\n"
            f"*·   DESCRIPCIÓN:* {TIEMPO[indice_tiempo]}\n\n"
            f"*·   NOVEDAD:* Sin novedades para la hora.\n\n"
            f"*·   REPORTA:* {operador_str}\n\n"
            f"*SOLO QUEREMOS SALVAR VIDAS 🚨🚑*"
        )
        
        return reporte
    
    @staticmethod
    def markdown_a_textspan(texto: str):
        """Convierte texto markdown simple (*texto*) a TextSpans de Flet."""
        import flet as ft
        from styles import Colors, FONT_FAMILY
        
        patron = r'(\*.*?\*)|([^\*]+)'
        spans = []
        
        for match in re.finditer(patron, texto):
            if match.group(1):  # Texto entre asteriscos (negrita)
                texto_negrita = match.group(1).strip('*')
                spans.append(
                    ft.TextSpan(
                        texto_negrita,
                        ft.TextStyle(
                            weight=ft.FontWeight.BOLD,
                            color=Colors.LIGHT["on_surface"],  # Se actualizará según el tema
                            font_family=FONT_FAMILY
                        )
                    )
                )
            elif match.group(2):  # Texto normal
                spans.append(
                    ft.TextSpan(
                        match.group(2),
                        ft.TextStyle(
                            color=Colors.LIGHT["on_surface"],  # Se actualizará según el tema
                            font_family=FONT_FAMILY
                        )
                    )
                )
        
        return spans

class AppState:
    """Estado global de la aplicación."""
    
    def __init__(self, page=None):
        self.page = page
        self.operador_manager = OperadorManager(page=self.page)
        self.alarm_manager = AlarmManager()
        self.indice_tiempo = 0
        self.indice_operador = 0
        self.is_dark_theme = False
        self.departamento = DEPARTAMENTO
        self.municipio = "Guanta"  # Valor por defecto
        self.cargar_configuracion()
        self._set_default_operator()

    def _set_default_operator(self):
        """Establece el operador por defecto."""
        default_operator_name = "Rubén Rojas"
        default_operator_index = self.operador_manager.obtener_indice_por_nombre(default_operator_name)
        if default_operator_index != -1:
            self.indice_operador = default_operator_index

    def cargar_configuracion(self):
        """Carga la configuración del usuario desde el almacenamiento del cliente."""
        if self.page and self.page.client_storage:
            self.departamento = self.page.client_storage.get("departamento") or self.departamento
            self.municipio = self.page.client_storage.get("municipio") or self.municipio

    def guardar_configuracion(self):
        """Guarda la configuración actual del usuario en el almacenamiento del cliente."""
        if self.page and self.page.client_storage:
            self.page.client_storage.set("departamento", self.departamento)
            self.page.client_storage.set("municipio", self.municipio)

    def obtener_operador_actual(self) -> Optional[Operador]:
        """Obtiene el operador actualmente seleccionado."""
        return self.operador_manager.obtener_operador_por_indice(self.indice_operador)
    
    def cambiar_operador(self, nombre: str) -> None:
        """Cambia el operador seleccionado por nombre."""
        indice = self.operador_manager.obtener_indice_por_nombre(nombre)
        if indice >= 0:
            self.indice_operador = indice
    
    def cambiar_tiempo(self, indice: int) -> None:
        """Cambia el índice del tiempo seleccionado."""
        if 0 <= indice < len(TIEMPO):
            self.indice_tiempo = indice
    
    def generar_reporte_actual(self) -> str:
        """Genera el reporte con el estado actual."""
        operador = self.obtener_operador_actual()
        return ReportGenerator.generar_reporte(
            self.indice_tiempo,
            operador,
            self.municipio,
            self.departamento
        )