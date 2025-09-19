# models.py
"""
Modelos de datos y lógica de negocio de la aplicación.
"""
import json
import datetime
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from config import TIEMPO, EMOJI_TIEMPO, DEPARTAMENTO, EJES

@dataclass
class Operador:
    """Modelo para representar un operador."""
    nombre: str
    cargo: str
    jerarquia: str
    cedula: str

    def __str__(self) -> str:
        return f"{self.jerarquia} {self.nombre} {self.cedula}"

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
    def generar_reporte_estadal(
        estados_municipios: Dict[str, str],
        operador: Optional[Operador]
    ) -> str:
        """Genera el reporte meteorológico para el estado."""
        fecha_actual = datetime.date.today().strftime('%d/%B/%Y').capitalize()
        hora_actual = datetime.datetime.now().strftime('%H:%M')
        operador_str = str(operador) if operador else "(Sin operador)"

        reporte_partes = [
            "*SISTEMA NACIONAL DE GESTIÓN DE RIESGO*",
            "*PROTECCIÓN CIVIL ANZOÁTEGUI*",
            f"- *FECHA:* {fecha_actual}",
            f"- *HORA:* {hora_actual} HLV",
            "- *REDAN:* Oriente",
            "- *ZOEDAN:* Anzoátegui",
            "",
            "*REPORTE METEOROLOGICO:*",
            ""
        ]

        for eje, municipios in EJES.items():
            reporte_partes.append(f"📌 *EJE {eje}*")
            for municipio in municipios:
                estado = estados_municipios.get(municipio, "No se obtuvo información")
                reporte_partes.append(f"- *{municipio.upper()}:* {estado}")
            reporte_partes.append("")

        reporte_partes.extend([
            f"- *REPORTA:* {operador_str}",
            "",
            "*SOLO QUEREMOS SALVAR VIDAS* 🚑"
        ])

        return "\n".join(reporte_partes)

    @staticmethod
    def markdown_a_textspan(texto: str):
        """Convierte texto markdown simple (*texto*) a TextSpans de Flet."""
        import flet as ft
        from styles import Colors, FONT_FAMILY

        patron = r'(\*.*?\*)|([^\*]+)'
        spans = []

        for match in re.finditer(patron, texto):
            if match.group(1):
                texto_negrita = match.group(1).strip('*')
                spans.append(
                    ft.TextSpan(
                        texto_negrita,
                        ft.TextStyle(
                            weight=ft.FontWeight.BOLD,
                            font_family=FONT_FAMILY
                        )
                    )
                )
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

        # Nuevo estado para los municipios
        self.estados_municipios: Dict[str, str] = {}
        self._inicializar_estados()

        self._set_default_operator()

    def _inicializar_estados(self):
        """Inicializa el estado del tiempo para todos los municipios."""
        estado_inicial = TIEMPO[0]  # Cielo despejado por defecto
        for eje, municipios in EJES.items():
            for municipio in municipios:
                self.estados_municipios[municipio] = estado_inicial

    def _set_default_operator(self):
        """Establece el operador por defecto."""
        default_operator_name = "Rubén Rojas"
        default_operator_index = self.operador_manager.obtener_indice_por_nombre(default_operator_name)
        if default_operator_index != -1:
            self.indice_operador = default_operator_index

    def obtener_operador_actual(self) -> Optional[Operador]:
        """Obtiene el operador actualmente seleccionado."""
        return self.operador_manager.obtener_operador_por_indice(self.indice_operador)

    def cambiar_operador(self, nombre: str) -> None:
        """Cambia el operador seleccionado por nombre."""
        indice = self.operador_manager.obtener_indice_por_nombre(nombre)
        if indice >= 0:
            self.indice_operador = indice

    def actualizar_estado_municipio(self, municipio: str, estado: str):
        """Actualiza el estado del tiempo de un municipio específico."""
        if municipio in self.estados_municipios:
            self.estados_municipios[municipio] = estado

    def generar_reporte_actual(self) -> str:
        """Genera el reporte con el estado actual."""
        operador = self.obtener_operador_actual()
        return ReportGenerator.generar_reporte_estadal(
            self.estados_municipios,
            operador
        )