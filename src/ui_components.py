# ui_components.py
"""
Componentes de interfaz de usuario reutilizables para la aplicación de reportes estadales.
"""
import flet as ft
import re
from typing import Callable, List
from models import AppState, Operador, ReportEntry
from styles import TextStyles, ButtonStyles, ContainerStyles, InputStyles, Colors, ThemeManager, Shadows
from config import NOMBRES_TIEMPO, TIEMPO, EMOJI_TIEMPO, JERARQUIAS, WINDOW_CONFIG, get_cargos

class ReportEntryRow(ft.ResponsiveRow):
    """Representa una única línea de entrada de reporte para un municipio, usando un layout responsivo."""
    def __init__(self, app_state: AppState, municipio: str, entry: ReportEntry, on_delete: Callable):
        super().__init__(spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        self.app_state = app_state
        self.municipio = municipio
        self.entry = entry
        self.on_delete_callback = on_delete
        self.page = app_state.page

        self._is_first_entry = self.app_state.estados_municipios[self.municipio][0].id == self.entry.id

        self.time_field = ft.TextField(
            label="Hora", value=self.entry.hora,
            on_blur=self._on_data_change,
            **InputStyles.textfield(self.app_state.is_dark_theme)
        )

        weather_options = [ft.dropdown.Option(key="-1", text="Selecciona una opción")] + [
            ft.dropdown.Option(key=str(i), text=f"{EMOJI_TIEMPO[i]} {nombre}") for i, nombre in enumerate(NOMBRES_TIEMPO)
        ]

        self.weather_dropdown = ft.Dropdown(
            options=weather_options,
            value=str(self.entry.indice_tiempo) if self.entry.indice_tiempo is not None else "-1",
            padding=ft.padding.symmetric(vertical=12, horizontal=10),
            on_change=self._on_data_change,
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )

        self.delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE, icon_color=Colors.ERROR,
            on_click=self._delete_clicked, visible=not self._is_first_entry, tooltip="Eliminar línea"
        )

        self.controls = [
            ft.Container(self.time_field, col={"xs": 4, "sm": 3}),
            ft.Container(self.weather_dropdown, col={"xs": 8, "sm": 7}),
            ft.Container(self.delete_button, col={"xs": 12, "sm": 2}),
        ]
        self._update_time_field_visibility()

    def _on_data_change(self, e=None):
        # Formatear el valor del campo de hora cuando pierde el foco
        if e and e.control == self.time_field:
            tf = self.time_field
            digits = "".join(filter(str.isdigit, tf.value))[:4]
            if len(digits) > 2:
                formatted_time = f"{digits[:2]}:{digits[2:]}"
            else:
                formatted_time = digits
            tf.value = formatted_time

        dropdown_val = self.weather_dropdown.value
        new_indice = int(dropdown_val) if dropdown_val and dropdown_val != "-1" else None

        self.app_state.update_report_line(
            self.municipio, self.entry.id, new_indice, self.time_field.value
        )

        self._update_time_field_visibility()

        # Actualización única al final
        if self.page: self.page.update()

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
        is_valid = self.weather_dropdown.value is not None and self.weather_dropdown.value != "-1"
        self.weather_dropdown.border_color = Colors.ERROR if not is_valid else None
        time_valid = True
        time_val = self.time_field.value
        if time_val:
            time_valid = False
            if re.match(r"^\d{2}:\d{2}$", time_val):
                try:
                    h, m = map(int, time_val.split(':'))
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        time_valid = True
                except ValueError: time_valid = False
        if not time_valid:
             self.time_field.error_text = "Hora inválida"
             is_valid = False
        else: self.time_field.error_text = None
        self.update()
        return is_valid

    def update_theme(self):
        """Actualiza el tema de la fila de entrada de reporte."""
        is_dark = self.app_state.is_dark_theme

        # Actualizar estilo del campo de hora
        time_field_style = InputStyles.textfield(is_dark)
        for key, value in time_field_style.items():
            setattr(self.time_field, key, value)

        # Actualizar estilo del dropdown de clima
        weather_dropdown_style = InputStyles.dropdown(is_dark)
        for key, value in weather_dropdown_style.items():
            setattr(self.weather_dropdown, key, value)

        # self.update() # Removido para la actualización por lotes

class EjeCard(ft.Container):
    def __init__(self, app_state: AppState, eje_nombre: str, municipios: List[str]):
        super().__init__()
        self.app_state = app_state
        self.eje_nombre = eje_nombre
        self.municipios = municipios
        self.entry_controls = {}

        card_style = ContainerStyles.card(self.app_state.is_dark_theme)
        self.padding = card_style.get("padding")
        self.bgcolor = card_style.get("bgcolor")
        self.border_radius = card_style.get("border_radius")
        self.shadow = card_style.get("shadow")

        self.content = self._build()

    def _build(self):
        self.title = ft.Text(f"📌 EJE {self.eje_nombre}", style=TextStyles.subtitle(self.app_state.is_dark_theme))
        header = ft.Column(
            controls=[
                self.title,
                ft.Divider(),
            ],
            spacing=5
        )
        municipio_cols = [self._create_municipio_view(m) for m in self.municipios]
        scrollable_content = ft.Column(controls=municipio_cols, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        return ft.Column(controls=[header, scrollable_content], expand=True)

    def _create_municipio_view(self, municipio: str) -> ft.Column:
        entries_container = ft.Column()
        self.entry_controls[municipio] = entries_container

        # Llenar el contenedor con las entradas existentes al inicio
        for entry in self.app_state.estados_municipios.get(municipio, []):
            entries_container.controls.append(
                ReportEntryRow(self.app_state, municipio, entry, on_delete=lambda e_id: self._delete_entry_row(municipio, e_id))
            )

        return ft.Column([
            ft.Row([
                ft.Text(municipio, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, on_click=lambda e, m=municipio: self._add_entry_row(m), tooltip="Añadir línea")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            entries_container,
            ft.Divider(height=5, thickness=0.5)
        ])

    def _add_entry_row(self, municipio: str):
        """Añade una nueva fila de entrada de forma eficiente."""
        new_entry = self.app_state.add_report_line(municipio)
        if new_entry:
            new_row = ReportEntryRow(self.app_state, municipio, new_entry, on_delete=lambda e_id: self._delete_entry_row(municipio, e_id))
            # Aplicar tema actual a la nueva fila
            new_row.update_theme()
            self.entry_controls[municipio].controls.append(new_row)
            if self.page: self.page.update()

    def _delete_entry_row(self, municipio: str, entry_id: str):
        """Elimina una fila de entrada de forma eficiente."""
        self.app_state.remove_report_line(municipio, entry_id)

        container = self.entry_controls[municipio]
        row_to_remove = next((row for row in container.controls if isinstance(row, ReportEntryRow) and row.entry.id == entry_id), None)

        if row_to_remove:
            container.controls.remove(row_to_remove)
            if self.page: self.page.update()

    def validate(self) -> bool:
        is_valid = True
        for entries_container in self.entry_controls.values():
            for row in entries_container.controls:
              if isinstance(row, ReportEntryRow) and not row.validate():
                is_valid = False
        return is_valid

    def update_theme(self):
        """Actualiza el tema de la tarjeta del eje y todos sus componentes hijos."""
        is_dark = self.app_state.is_dark_theme

        # Actualizar estilos del contenedor principal
        card_style = ContainerStyles.card(is_dark)
        self.bgcolor = card_style.get("bgcolor")
        self.shadow = card_style.get("shadow")

        # Actualizar estilo del título
        self.title.style = TextStyles.subtitle(is_dark)

        # Actualizar el tema de cada fila de entrada de reporte
        for municipio_container in self.entry_controls.values():
            for row in municipio_container.controls:
                if isinstance(row, ReportEntryRow):
                    row.update_theme()

        # self.update() # Removido para la actualización por lotes

class CustomAppBar:
    def __init__(self, app_state: AppState, on_theme_change: Callable, on_manage_operators: Callable):
        self.app_state = app_state
        self.on_theme_change = on_theme_change
        self.on_manage_operators = on_manage_operators
        self.app_bar = self._create_app_bar()

    def _create_app_bar(self) -> ft.AppBar:
        is_dark = self.app_state.is_dark_theme
        title_row = ft.Row(
            [
                ft.Image(src="icon.png", width=40, height=40),
                ft.Text(WINDOW_CONFIG["title"], style=TextStyles.subtitle(is_dark), no_wrap=True, expand=True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
        return ft.AppBar(
            leading_width=0, title=title_row, bgcolor=ContainerStyles.card(is_dark)["bgcolor"],
            actions=[
                ft.PopupMenuButton(items=[
                    ft.PopupMenuItem(text="Cambiar Tema", icon=ThemeManager.get_theme_icon(is_dark), on_click=lambda _: self.on_theme_change()),
                    ft.PopupMenuItem(text="Gestionar Operadores", icon=ft.Icons.MANAGE_ACCOUNTS, on_click=lambda _: self.on_manage_operators()),
                    ft.PopupMenuItem(text="Acerca de", icon=ft.Icons.INFO_OUTLINE, on_click=self._show_about_dialog),
                ]),
            ],
        )

    def _show_about_dialog(self, e):
        """Muestra el diálogo 'Acerca de'."""
        is_dark = self.app_state.is_dark_theme
        dialog_style = ContainerStyles.dialog(is_dark)

        about_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Acerca de", style=TextStyles.subtitle(is_dark)),
            content=ft.Column(
                [
                    ft.Image(src="icon.png", width=150, height=150),
                    ft.Text("Creado por:", style=TextStyles.body(is_dark)),
                    ft.Text("Rubén Rojas", weight=ft.FontWeight.BOLD, size=16),
                    ft.Text("Versión 1.0.0", style=TextStyles.caption(is_dark)),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                width=300,
                height=300,
            ),
            actions=[
                ft.ElevatedButton(
                    "Cerrar",
                    on_click=lambda e: self.app_state.page.close(about_dialog),
                    style=ButtonStyles.secondary(is_dark)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor=dialog_style.get("bgcolor"),
            shape=ft.RoundedRectangleBorder(radius=dialog_style.get("border_radius", 0))
        )
        self.app_state.page.open(about_dialog)

    def update_theme(self):
        is_dark = self.app_state.is_dark_theme
        # El título es el segundo control en la fila del título
        title_text = self.app_bar.title.controls[1]
        title_text.style = TextStyles.subtitle(is_dark)

        self.app_bar.bgcolor = ContainerStyles.card(is_dark)["bgcolor"]

        # Actualizar el menú emergente
        popup_menu = self.app_bar.actions[0]
        popup_menu.items[0].text = "Cambiar Tema"
        popup_menu.items[0].icon = ThemeManager.get_theme_icon(is_dark)

        # self.app_bar.update() # Removido para la actualización por lotes

class OperatorSelector(ft.Dropdown):
    def __init__(self, app_state: AppState, on_change: Callable):
        self.app_state = app_state
        self.on_change_callback = on_change
        nombres = self.app_state.operador_manager.obtener_nombres()
        valor_inicial = nombres[self.app_state.indice_operador] if nombres else None
        super().__init__(
            label="Operador que reporta", options=[ft.dropdown.Option(nombre) for nombre in nombres],
            value=valor_inicial, on_change=self._on_dropdown_change,
            **InputStyles.dropdown(self.app_state.is_dark_theme)
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
        # self.update() # Removido para la actualización por lotes

class OperatorManagementDialog:
    def __init__(self, app_state: AppState, operator_selector: OperatorSelector, page: ft.Page):
        self.app_state = app_state
        self.operator_selector = operator_selector
        self.page = page
        self.dialog = None

    def _format_cedula(self, e):
        """Formatea la cédula mientras el usuario escribe."""
        control = e.control

        # Limpiar el valor para obtener solo los dígitos
        digits = "".join(filter(str.isdigit, control.value))

        # Limitar a 8 dígitos (máximo para cédulas en Venezuela)
        if len(digits) > 8:
            digits = digits[:8]

        # Formatear los dígitos con puntos
        if len(digits) > 5:
            formatted_digits = f"{digits[:-6]}.{digits[-6:-3]}.{digits[-3:]}"
        elif len(digits) > 2:
            formatted_digits = f"{digits[:-3]}.{digits[-3:]}"
        else:
            formatted_digits = digits

        # Construir el valor final con el prefijo "V-"
        new_value = f"V-{formatted_digits}" if digits else "V-"

        # Actualizar el control solo si el valor ha cambiado para evitar bucles
        if control.value != new_value:
            control.value = new_value
            control.update()


    def _create_form_fields(self):
        style = InputStyles.textfield(self.app_state.is_dark_theme)
        self.nombre_field = ft.TextField(label="Nombre", hint_text="Nombre del operador",  **style)
        self.cedula_field = ft.TextField(label="Cédula", hint_text="V-XX.XXX.XXX", on_change=self._format_cedula, **style)
        cargos = get_cargos(self.app_state.departamento)
        self.cargo_dropdown = ft.Dropdown(label="Cargo", options=[ft.dropdown.Option(c) for c in cargos], value=cargos[0] if cargos else None, **InputStyles.dropdown(self.app_state.is_dark_theme))
        self.jerarquia_dropdown = ft.Dropdown(label="Jerarquía", options=[ft.dropdown.Option(j) for j in JERARQUIAS], value=JERARQUIAS[0], **InputStyles.dropdown(self.app_state.is_dark_theme))
        self.eliminar_dropdown = ft.Dropdown(label="Eliminar operador", options=[ft.dropdown.Option(n) for n in self.app_state.operador_manager.obtener_nombres()], **InputStyles.dropdown(self.app_state.is_dark_theme))

    def show(self, e=None):
        self._create_form_fields()
        is_dark = self.app_state.is_dark_theme
        dialog_style = ContainerStyles.dialog(is_dark)

        # Crear los botones con el estilo de tema correcto
        add_button = ft.ElevatedButton("Añadir", on_click=self._agregar_operador, style=ButtonStyles.primary())
        delete_button = ft.ElevatedButton("Eliminar", on_click=self._eliminar_operador, style=ButtonStyles.danger())
        close_button = ft.ElevatedButton("Cerrar", on_click=self._cerrar_dialog, style=ButtonStyles.secondary(is_dark))

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Gestión de Operadores", style=TextStyles.subtitle(is_dark)),
            content=ft.Column([
                self.nombre_field, self.cedula_field, self.cargo_dropdown, self.jerarquia_dropdown,
                ft.Row([add_button], alignment="center"),
                ft.Divider(),
                self.eliminar_dropdown,
                ft.Row([delete_button], alignment="center")
            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10, tight=True),
            actions=[close_button],
            actions_alignment="center",
            bgcolor=dialog_style.get("bgcolor"),
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