# ui_components.py
"""
Componentes de interfaz de usuario reutilizables para la aplicación de reportes estadales.
"""
import flet as ft
import re
from typing import Callable, List
from models import AppState, Operador, ReportEntry
from styles import TextStyles, ButtonStyles, ContainerStyles, InputStyles, Colors, ThemeManager
from config import NOMBRES_TIEMPO, TIEMPO, EMOJI_TIEMPO, JERARQUIAS, WINDOW_CONFIG, get_cargos

class MunicipalityEntry(ft.Row):
    """Representa la línea de entrada de reporte para un único municipio."""
    def __init__(self, app_state: AppState, municipio: str):
        super().__init__(vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        self.app_state = app_state
        self.municipio = municipio
        self.entry = self.app_state.estados_municipios[self.municipio]

        self.weather_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(key=str(i), text=f"{EMOJI_TIEMPO[i]} {nombre}") for i, nombre in enumerate(NOMBRES_TIEMPO)],
            value=str(self.entry.indice_tiempo),
            width=200,
            on_change=self._on_data_change,
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )

        self.time_field = ft.TextField(
            value=self.entry.hora or "00:00",
            width=120,
            hint_text="HH:MM",
            suffix_text="HLV",
            on_blur=self._on_data_change,
            on_change=self._clean_time_input,
            **InputStyles.textfield(self.app_state.is_dark_theme)
        )

        self.controls = [
            ft.Text(self.municipio, weight=ft.FontWeight.BOLD, expand=True),
            self.weather_dropdown,
            self.time_field,
        ]

    def _clean_time_input(self, e):
        """Limpia y formatea la entrada del campo de tiempo mientras se escribe."""
        tf = e.control
        # Allow only digits and one colon
        clean_value = "".join(filter(lambda char: char.isdigit() or char == ':', tf.value))
        if clean_value.count(':') > 1:
            parts = clean_value.split(':', 2)
            clean_value = parts[0] + ":" + "".join(parts[1:])
        tf.value = clean_value[:5]  # Max length HH:MM
        tf.update()

    def _on_data_change(self, e=None):
        """Actualiza el estado de la aplicación cuando cambia un valor."""
        # Remove suffix before saving to model
        time_value = self.time_field.value.replace(" HLV", "").strip()
        self.app_state.update_report_line(
            self.municipio,
            int(self.weather_dropdown.value),
            time_value
        )

    def validate(self) -> bool:
        """Valida los campos de entrada de esta fila."""
        # Weather validation
        is_valid = self.weather_dropdown.value != "0"
        self.weather_dropdown.border_color = Colors.ERROR if not is_valid else None

        # Time validation
        time_valid = False
        time_val = self.time_field.value
        if re.match(r"^\d{2}:\d{2}$", time_val):
            try:
                h, m = map(int, time_val.split(':'))
                if 0 <= h <= 23 and 0 <= m <= 59:
                    time_valid = True
            except ValueError:
                time_valid = False

        if not time_valid:
            self.time_field.error_text = "Hora inválida"
            is_valid = False
        else:
            self.time_field.error_text = None

        self.update()
        return is_valid

class EjeCard(ft.Container):
    """Tarjeta que contiene los controles para un eje geográfico."""
    def __init__(self, app_state: AppState, eje_nombre: str, municipios: List[str]):
        super().__init__()
        self.app_state = app_state
        self.eje_nombre = eje_nombre
        self.municipios = municipios
        self.padding = ContainerStyles.card(self.app_state.is_dark_theme).get("padding")
        self.bgcolor = ContainerStyles.card(self.app_state.is_dark_theme).get("bgcolor")
        self.border_radius = ContainerStyles.card(self.app_state.is_dark_theme).get("border_radius")

        self.municipio_controls = []
        self.content = self._build()

    def _build(self):
        """Construye el contenido de la tarjeta del eje."""
        municipio_entries = []
        for municipio in self.municipios:
            entry_row = MunicipalityEntry(self.app_state, municipio)
            municipio_entries.append(entry_row)
            municipio_entries.append(ft.Divider(height=5, thickness=0.5))

        if municipio_entries:
            municipio_entries.pop()  # Remove the last divider

        self.municipio_controls = municipio_entries

        return ft.Column(
            [ft.Text(f"📌 EJE {self.eje_nombre}", style=TextStyles.subtitle(self.app_state.is_dark_theme)), ft.Divider()] + self.municipio_controls,
            expand=True,
            scroll=ft.ScrollMode.HIDDEN
        )

    def validate(self) -> bool:
        """Valida todas las entradas de los municipios en esta tarjeta."""
        is_valid = True
        for control in self.municipio_controls:
            if isinstance(control, MunicipalityEntry) and not control.validate():
                is_valid = False
        return is_valid

# --- Componentes restantes (CustomAppBar, OperatorSelector, etc.) ---

class CustomAppBar:
    def __init__(self, app_state: AppState, on_theme_change: Callable, on_manage_operators: Callable, operator_selector: 'OperatorSelector', on_copy: Callable):
        self.app_state = app_state
        self.on_theme_change = on_theme_change
        self.on_manage_operators = on_manage_operators
        self.operator_selector = operator_selector
        self.on_copy = on_copy
        self.app_bar = self._create_app_bar()

    def _create_app_bar(self) -> ft.AppBar:
        is_dark = self.app_state.is_dark_theme
        self.operator_selector.width = 300
        self.operator_selector.label = ""
        self.operator_selector.hint_text = "Operador que reporta"

        title_row = ft.Row(
            [
                ft.Image(src="icon.png", width=30, height=30),
                ft.Text(WINDOW_CONFIG["title"], style=TextStyles.subtitle(is_dark)),
                self.operator_selector,
            ],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

        copy_button = ft.IconButton(
            icon=ft.Icons.CONTENT_COPY,
            tooltip="Copiar al Portapapeles",
            on_click=lambda _: self.on_copy()
        )

        return ft.AppBar(
            leading_width=0,
            title=title_row,
            bgcolor=ContainerStyles.card(is_dark)["bgcolor"],
            actions=[
                copy_button,
                ft.PopupMenuButton(items=[
                    ft.PopupMenuItem(text="Cambiar Tema", icon=ThemeManager.get_theme_icon(is_dark), on_click=lambda _: self.on_theme_change()),
                    ft.PopupMenuItem(text="Gestionar Operadores", icon=ft.Icons.MANAGE_ACCOUNTS, on_click=lambda _: self.on_manage_operators()),
                ]),
            ],
        )

    def update_theme(self):
        is_dark = self.app_state.is_dark_theme
        title_text = self.app_bar.title.controls[1]
        title_text.style = TextStyles.subtitle(is_dark)
        self.app_bar.bgcolor = ContainerStyles.card(is_dark)["bgcolor"]
        # The PopupMenu is now the second action
        self.app_bar.actions[1].items[0].icon = ThemeManager.get_theme_icon(is_dark)
        self.operator_selector.update_theme()


class OperatorSelector(ft.Dropdown):
    def __init__(self, app_state: AppState, on_change: Callable):
        self.app_state = app_state
        self.on_change_callback = on_change
        nombres = self.app_state.operador_manager.obtener_nombres()
        valor_inicial = nombres[self.app_state.indice_operador] if nombres else None
        super().__init__(
            label="Operador que reporta", options=[ft.dropdown.Option(nombre) for nombre in nombres],
            value=valor_inicial, on_change=self._on_dropdown_change,
            **InputStyles.dropdown(self.app_state.is_dark_theme), width=400
        )

    def _on_dropdown_change(self, e):
        if e.control.value:
            self.app_state.cambiar_operador(e.control.value)
            self.on_change_callback()

    def refresh_options(self):
        nombres = self.app_state.operador_manager.obtener_nombres()
        self.options = [ft.dropdown.Option(nombre) for nombre in nombres]
        self.value = nombres[self.app_state.indice_operador] if nombres and 0 <= self.app_state.indice_operador < len(nombres) else None
        self.update()

    def update_theme(self):
        style = InputStyles.dropdown(self.app_state.is_dark_theme)
        for key, value in style.items():
            setattr(self, key, value)
        self.update()


class OperatorManagementDialog:
    def __init__(self, app_state: AppState, operator_selector: OperatorSelector, page: ft.Page):
        self.app_state = app_state
        self.operator_selector = operator_selector
        self.page = page
        self.dialog = None

    def _create_form_fields(self):
        style = InputStyles.textfield(self.app_state.is_dark_theme)
        self.nombre_field = ft.TextField(label="Nombre", width=300, hint_text="Nombre del operador", **style)
        self.cedula_field = ft.TextField(label="Cédula", width=300, hint_text="V-XX.XXX.XXX", **style)
        cargos = get_cargos(self.app_state.departamento)
        self.cargo_dropdown = ft.Dropdown(label="Cargo", width=300, options=[ft.dropdown.Option(c) for c in cargos], value=cargos[0] if cargos else None, **InputStyles.dropdown(self.app_state.is_dark_theme))
        self.jerarquia_dropdown = ft.Dropdown(label="Jerarquía", width=300, options=[ft.dropdown.Option(j) for j in JERARQUIAS], value=JERARQUIAS[0], **InputStyles.dropdown(self.app_state.is_dark_theme))
        self.eliminar_dropdown = ft.Dropdown(label="Eliminar operador", width=300, options=[ft.dropdown.Option(n) for n in self.app_state.operador_manager.obtener_nombres()], **InputStyles.dropdown(self.app_state.is_dark_theme))

    def show(self, e=None):
        self._create_form_fields()
        dialog_style = ContainerStyles.dialog(self.app_state.is_dark_theme)
        self.dialog = ft.AlertDialog(
            modal=True, title=ft.Text("Gestión de Operadores", style=TextStyles.subtitle(self.app_state.is_dark_theme)),
            content=ft.Column([
                self.nombre_field, self.cedula_field, self.cargo_dropdown, self.jerarquia_dropdown,
                ft.Row([ft.ElevatedButton("Añadir", on_click=self._agregar_operador, style=ButtonStyles.primary())], alignment="center"),
                ft.Divider(), self.eliminar_dropdown,
                ft.Row([ft.ElevatedButton("Eliminar", on_click=self._eliminar_operador, style=ButtonStyles.danger())], alignment="center")
            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10, width=300, height=400),
            actions=[ft.ElevatedButton("Cerrar", on_click=self._cerrar_dialog, style=ButtonStyles.secondary(self.app_state.is_dark_theme))],
            actions_alignment="center", bgcolor=dialog_style.get("bgcolor"),
            shape=ft.RoundedRectangleBorder(radius=dialog_style.get("border_radius", 0))
        )
        self.page.open(self.dialog)

    def _agregar_operador(self, e):
        if self.app_state.operador_manager.agregar_operador(self.nombre_field.value.strip(), self.cargo_dropdown.value, self.jerarquia_dropdown.value, self.cedula_field.value.strip()):
            self.operator_selector.refresh_options()
            self._refresh_delete_dropdown()
            self.nombre_field.value, self.cedula_field.value = "", ""
            self._show_snackbar("Operador añadido", Colors.SUCCESS)
        else: self._show_snackbar("Error: Verifique los datos o si el operador ya existe", Colors.ERROR)
        self.page.update()

    def _eliminar_operador(self, e):
        if self.eliminar_dropdown.value and self.app_state.operador_manager.eliminar_operador(self.eliminar_dropdown.value):
            self.operator_selector.refresh_options()
            self._refresh_delete_dropdown()
            self._show_snackbar("Operador eliminado", Colors.WARNING)
        else: self._show_snackbar("Error al eliminar operador", Colors.ERROR)
        self.page.update()

    def _refresh_delete_dropdown(self):
        self.eliminar_dropdown.options = [ft.dropdown.Option(n) for n in self.app_state.operador_manager.obtener_nombres()]
        self.eliminar_dropdown.value = None
        self.dialog.content.update()

    def _cerrar_dialog(self, e): self.page.close(self.dialog)
    def _show_snackbar(self, m: str, c): self.page.open(ft.SnackBar(ft.Text(m, color=c)))