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

class ReportEntryRow(ft.Row):
    """Representa una única línea de entrada de reporte para un municipio."""
    def __init__(self, app_state: AppState, municipio: str, entry: ReportEntry, on_delete: Callable):
        super().__init__(spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        self.app_state = app_state
        self.municipio = municipio
        self.entry = entry
        self.on_delete_callback = on_delete
        self.page = app_state.page # For updates

        self._is_first_entry = self.app_state.estados_municipios[self.municipio][0].id == self.entry.id

        self.time_field = ft.TextField(
            label="Hora", width=80, value=self.entry.hora,
            on_blur=self._on_data_change,
            on_change=self._on_time_change, # Time formatting
            **InputStyles.textfield(self.app_state.is_dark_theme)
        )

        weather_options = [ft.dropdown.Option(key="-1", text="-- Seleccione Clima --")] + [
            ft.dropdown.Option(key=str(i), text=f"{EMOJI_TIEMPO[i]} {nombre}") for i, nombre in enumerate(NOMBRES_TIEMPO)
        ]

        self.weather_dropdown = ft.Dropdown(
            options=weather_options,
            value=str(self.entry.indice_tiempo) if self.entry.indice_tiempo is not None else "-1",
            width=240,
            on_change=self._on_data_change,
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )

        self.delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE, icon_color=Colors.ERROR,
            on_click=self._delete_clicked, visible=not self._is_first_entry, tooltip="Eliminar línea"
        )

        self.controls = [self.time_field, self.weather_dropdown, self.delete_button]
        self._update_time_field_visibility()

    def _on_time_change(self, e):
        """Auto-formats the time field to HH:MM and limits digits."""
        tf = e.control
        digits = "".join(filter(str.isdigit, tf.value))[:4]
        if len(digits) > 2:
            formatted_time = f"{digits[:2]}:{digits[2:]}"
        else:
            formatted_time = digits
        if tf.value != formatted_time:
            tf.value = formatted_time
            tf.update()

    def _on_data_change(self, e=None):
        dropdown_val = self.weather_dropdown.value
        new_indice = int(dropdown_val) if dropdown_val and dropdown_val != "-1" else None

        self.app_state.update_report_line(
            self.municipio, self.entry.id,
            new_indice, self.time_field.value
        )
        self._update_time_field_visibility()
        if self.page:
            self.page.update()

    def _update_time_field_visibility(self):
        dropdown_val = self.weather_dropdown.value
        indice = int(dropdown_val) if dropdown_val and dropdown_val != "-1" else None

        if indice is None:
            self.time_field.visible = not self._is_first_entry
            return

        selected_text = TIEMPO[indice].lower()
        is_precipitation = "precipitaciones" in selected_text
        self.time_field.visible = not self._is_first_entry or is_precipitation

    def _delete_clicked(self, e):
        self.on_delete_callback(self.entry.id)

    def validate(self) -> bool:
        # Weather validation
        is_valid = self.weather_dropdown.value is not None and self.weather_dropdown.value != "-1"
        self.weather_dropdown.border_color = Colors.ERROR if not is_valid else None

        # Time validation
        time_valid = True # Assume valid if empty
        time_val = self.time_field.value
        if time_val: # Only validate if not empty
            time_valid = False
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
        self.entry_controls = {} # Almacena las columnas de entradas por municipio

        # Configuración del contenedor principal
        self.padding = ContainerStyles.card(self.app_state.is_dark_theme).get("padding")
        self.bgcolor = ContainerStyles.card(self.app_state.is_dark_theme).get("bgcolor")
        self.border_radius = ContainerStyles.card(self.app_state.is_dark_theme).get("border_radius")

        self.content = self._build()

    def _build(self):
        municipio_cols = [self._create_municipio_view(m) for m in self.municipios]
        return ft.Column(
            [ft.Text(f"📌 EJE {self.eje_nombre}", style=TextStyles.subtitle(self.app_state.is_dark_theme)), ft.Divider()] + municipio_cols,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True
        )

    def _create_municipio_view(self, municipio: str) -> ft.Column:
        entries_container = ft.Column()
        self.entry_controls[municipio] = entries_container
        self._rebuild_entries(municipio)

        def add_entry(e):
            self.app_state.add_report_line(municipio)
            self._rebuild_entries(municipio)
            self.update()

        return ft.Column([
            ft.Row([
                ft.Text(municipio, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, on_click=add_entry, tooltip="Añadir línea")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            entries_container,
            ft.Divider(height=5, thickness=0.5)
        ], expand=True)

    def _rebuild_entries(self, municipio: str):
        container = self.entry_controls[municipio]
        container.controls.clear()
        for entry in self.app_state.estados_municipios.get(municipio, []):
            row = ReportEntryRow(
                self.app_state, municipio, entry,
                on_delete=lambda entry_id: self._delete_entry(municipio, entry_id)
            )
            container.controls.append(row)

    def _delete_entry(self, municipio: str, entry_id: str):
        self.app_state.remove_report_line(municipio, entry_id)
        self._rebuild_entries(municipio)
        self.update()

    def validate(self) -> bool:
        is_valid = True
        for municipio_container in self.entry_controls.values():
            for row in municipio_container.controls:
                if isinstance(row, ReportEntryRow) and not row.validate():
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

        copy_button = ft.FilledButton(
            text="Copiar",
            icon=ft.icons.CONTENT_COPY,
            on_click=lambda _: self.on_copy(),
            style=ButtonStyles.primary()
        )

        # --- Title Row with Spacer ---
        self.operator_selector.width = 300
        self.operator_selector.label = ""
        self.operator_selector.hint_text = "Operador que reporta"

        title_row = ft.Row(
            [
                ft.Image(src="icon.png", width=30, height=30),
                ft.Text(WINDOW_CONFIG["title"], style=TextStyles.subtitle(is_dark)),
                ft.Container(expand=True),  # Spacer
                self.operator_selector
            ],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
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

        # Update theme icon in PopupMenu
        self.app_bar.actions[1].items[0].icon = ThemeManager.get_theme_icon(is_dark)

        # Update copy button style
        self.app_bar.actions[0].style = ButtonStyles.primary()

        # Update operator selector theme
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