# models.py
"""
Modelos de datos y lógica de negocio de la aplicación.
"""
import json
import os
import datetime
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from config import OPERADORES_FILE, TIEMPO, EMOJI_TIEMPO

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
    
    def __init__(self):
        self._operadores: List[Operador] = []
        self.cargar_operadores()
    
    def cargar_operadores(self) -> None:
        """Carga los operadores desde el archivo JSON."""
        if os.path.exists(OPERADORES_FILE):
            try:
                with open(OPERADORES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._operadores = [Operador.from_dict(op) for op in data]
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error cargando operadores: {e}")
                self._operadores = []
    
    def guardar_operadores(self) -> None:
        """Guarda los operadores en el archivo JSON."""
        try:
            with open(OPERADORES_FILE, "w", encoding="utf-8") as f:
                data = [op.to_dict() for op in self._operadores]
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error guardando operadores: {e}")
    
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

class ReportGenerator:
    """Generador de reportes meteorológicos."""
    
    @staticmethod
    def generar_reporte(indice_tiempo: int, operador: Optional[Operador]) -> str:
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
            f"*PROTECCIÓN CIVIL MUNICIPIO GUANTA* 🚨\n\n"
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
    
    def __init__(self):
        self.operador_manager = OperadorManager()
        self.indice_tiempo = 0
        self.indice_operador = 0
        self.is_dark_theme = False
    
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
        return ReportGenerator.generar_reporte(self.indice_tiempo, operador)