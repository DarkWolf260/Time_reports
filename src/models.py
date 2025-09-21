# models.py
"""
Modelos de datos y lógica de negocio de la aplicación.
"""
import json
import datetime
import re
import uuid
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from config import TIEMPO, DEPARTAMENTO, EJES

@dataclass
class ReportEntry:
    """Modelo para una línea de reporte de un municipio."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    indice_tiempo: Optional[int] = None
    hora: str = "" # e.g., "14:30"

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "indice_tiempo": self.indice_tiempo, "hora": self.hora}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportEntry':
        return cls(id=data.get("id", str(uuid.uuid4())), indice_tiempo=data.get("indice_tiempo", None), hora=data.get("hora", ""))

@dataclass
class Operador:
    """Modelo para representar un operador."""
    nombre: str
    cargo: str
    jerarquia: str
    cedula: str

    def __str__(self) -> str:
        return f"{self.jerarquia} {self.nombre} ({self.cargo})"

    def to_dict(self) -> Dict[str, str]:
        return {"nombre": self.nombre, "cargo": self.cargo, "jerarquia": self.jerarquia, "cedula": self.cedula}

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
        if self.page and self.page.client_storage:
            try:
                data_str = self.page.client_storage.get("operators")
                if data_str:
                    data = json.loads(data_str)
                    self._operadores = [Operador.from_dict(op) for op in data]
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error cargando operadores desde client_storage: {e}")

    def guardar_operadores(self) -> None:
        if self.page and self.page.client_storage:
            data = [op.to_dict() for op in self._operadores]
            self.page.client_storage.set("operators", json.dumps(data))

    def agregar_operador(self, nombre: str, cargo: str, jerarquia: str, cedula: str) -> bool:
        if not all([nombre.strip(), cargo, jerarquia, cedula.strip()]): return False
        if self.buscar_por_nombre(nombre.strip()) or self.buscar_por_cedula(cedula.strip()): return False
        operador = Operador(nombre.strip(), cargo, jerarquia, cedula.strip())
        self._operadores.append(operador)
        self.guardar_operadores()
        return True

    def eliminar_operador(self, nombre: str) -> bool:
        operador = self.buscar_por_nombre(nombre)
        if operador:
            self._operadores.remove(operador)
            self.guardar_operadores()
            return True
        return False

    def buscar_por_nombre(self, nombre: str) -> Optional[Operador]:
        return next((op for op in self._operadores if op.nombre == nombre), None)

    def buscar_por_cedula(self, cedula: str) -> Optional[Operador]:
        return next((op for op in self._operadores if op.cedula == cedula), None)

    def obtener_nombres(self) -> List[str]:
        return [op.nombre for op in self._operadores]

    def obtener_operador_por_indice(self, indice: int) -> Optional[Operador]:
        if 0 <= indice < len(self._operadores):
            return self._operadores[indice]
        return None

    def obtener_indice_por_nombre(self, nombre: str) -> int:
        for i, op in enumerate(self._operadores):
            if op.nombre == nombre:
                return i
        return -1

    @property
    def cantidad(self) -> int:
        return len(self._operadores)

class ReportGenerator:
    """Generador de reportes meteorológicos."""
    @staticmethod
    def generar_reporte_estadal(estados_municipios: Dict[str, List[ReportEntry]], operador: Optional[Operador]) -> str:
        fecha_actual = datetime.date.today().strftime('%d/%B/%Y').capitalize()
        hora_actual = datetime.datetime.now().strftime('%H:%M')
        operador_str = str(operador) if operador else "(Sin operador)"

        reporte_partes = [
            "*SISTEMA NACIONAL DE GESTIÓN DE RIESGO*", "*PROTECCIÓN CIVIL ANZOÁTEGUI*",
            f"- *FECHA:* {fecha_actual}", f"- *HORA:* {hora_actual} HLV",
            "- *REDAN:* Oriente", "- *ZOEDAN:* Anzoátegui", "",
            "*REPORTE METEOROLOGICO:*", ""
        ]

        for eje, municipios in EJES.items():
            reporte_partes.append(f"📌 *EJE {eje}*")
            for i, municipio in enumerate(municipios):
                entries = estados_municipios.get(municipio, [])
                if not entries:
                    reporte_partes.append(f"- *{municipio.upper()}:* No se obtuvo información")
                else:
                    # Primera línea
                    first_entry = entries[0]
                    estado_texto = TIEMPO[first_entry.indice_tiempo] if first_entry.indice_tiempo is not None else "Sin información"

                    # Lógica para la primera línea con o sin hora
                    if first_entry.hora and len(entries) == 1:
                         # Caso especial: una sola entrada con hora, sin formato markdown para la hora
                        reporte_partes.append(f"- *{municipio.upper()}:* {first_entry.hora} HLV - {estado_texto}")
                    else:
                        reporte_partes.append(f"- *{municipio.upper()}:* {estado_texto}")

                    # Líneas subsecuentes
                    for entry in entries[1:]:
                        estado_texto_sec = TIEMPO[entry.indice_tiempo] if entry.indice_tiempo is not None else "Sin información"
                        hora_str = f"{entry.hora} HLV" if entry.hora else ""
                        reporte_partes.append(f"- *{hora_str}:* {estado_texto_sec}")

                # Añadir separador entre municipios, excepto para el último
                if i < len(municipios) - 1:
                    reporte_partes.append("") # Separador cambiado a línea en blanco

            reporte_partes.append("")

        reporte_partes.extend([f"- *REPORTA:* {operador_str}", "", "*SOLO QUEREMOS SALVAR VIDAS* 🚑"])
        return "\n".join(reporte_partes)

    @staticmethod
    def markdown_a_textspan(texto: str):
        import flet as ft
        from styles import Colors, FONT_FAMILY
        patron = r'(\*.*?\*)|([^\*]+)'
        spans = []
        for match in re.finditer(patron, texto):
            if match.group(1):
                spans.append(ft.TextSpan(match.group(1).strip('*'), ft.TextStyle(weight=ft.FontWeight.BOLD, font_family=FONT_FAMILY)))
            elif match.group(2):
                spans.append(ft.TextSpan(match.group(2), ft.TextStyle(font_family=FONT_FAMILY)))
        return spans

class AppState:
    """Estado global de la aplicación."""
    def __init__(self, page=None):
        self.page = page
        self.operador_manager = OperadorManager(page=self.page)
        self.indice_operador = 0
        self.is_dark_theme = False
        self.departamento = DEPARTAMENTO
        self.estados_municipios: Dict[str, List[ReportEntry]] = {}
        self._inicializar_estados()
        self._set_default_operator()

    def _inicializar_estados(self):
        """Inicializa el estado con una entrada por defecto para cada municipio."""
        for eje, municipios in EJES.items():
            for municipio in municipios:
                self.estados_municipios[municipio] = [ReportEntry()]

    def add_report_line(self, municipio: str) -> Optional[ReportEntry]:
        if municipio in self.estados_municipios:
            new_entry = ReportEntry()
            self.estados_municipios[municipio].append(new_entry)
            return new_entry
        return None

    def update_report_line(self, municipio: str, line_id: str, new_indice: Optional[int], new_hora: str):
        if municipio in self.estados_municipios:
            for entry in self.estados_municipios[municipio]:
                if entry.id == line_id:
                    entry.indice_tiempo = new_indice
                    entry.hora = new_hora
                    break

    def remove_report_line(self, municipio: str, line_id: str):
        if municipio in self.estados_municipios and len(self.estados_municipios[municipio]) > 1:
            self.estados_municipios[municipio] = [entry for entry in self.estados_municipios[municipio] if entry.id != line_id]

    def _set_default_operator(self):
        default_operator_name = "Rubén Rojas"
        default_operator_index = self.operador_manager.obtener_indice_por_nombre(default_operator_name)
        if default_operator_index != -1:
            self.indice_operador = default_operator_index

    def obtener_operador_actual(self) -> Optional[Operador]:
        return self.operador_manager.obtener_operador_por_indice(self.indice_operador)

    def cambiar_operador(self, nombre: str) -> None:
        indice = self.operador_manager.obtener_indice_por_nombre(nombre)
        if indice >= 0:
            self.indice_operador = indice

    def generar_reporte_actual(self) -> str:
        operador = self.obtener_operador_actual()
        return ReportGenerator.generar_reporte_estadal(self.estados_municipios, operador)