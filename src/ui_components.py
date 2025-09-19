# ui_components.py
"""
Componentes de interfaz de usuario reutilizables para la aplicación de reportes estadales.
"""
import flet as ft
import json
from typing import Callable, List, Dict
from models import AppState, Operador
from styles import (
    TextStyles, ButtonStyles, ContainerStyles, InputStyles,
    Colors, ThemeManager
)
from config import NOMBRES_TIEMPO, TIEMPO, EMOJI_TIEMPO, JERARQUIAS, WINDOW_CONFIG, get_cargos


class CustomAppBar:
    """AppBar personalizada con título y menú de opciones."""

    def __init__(self, app_state: AppState, on_theme_change: Callable, on_manage_operators: Callable):
        self.app_state = app_state
        self.on_theme_change = on_theme_change
        self.on_manage_operators = on_manage_operators
        self.app_bar = self._create_app_bar()

    def _create_app_bar(self) -> ft.AppBar:
        """Crea el widget AppBar."""
        is_dark = self.app_state.is_dark_theme
        return ft.AppBar(
            leading=ft.Image(src="icon.png", width=30, height=30),
            title=ft.Text(
                WINDOW_CONFIG["title"],
                style=TextStyles.subtitle(is_dark)
            ),
            bgcolor=ContainerStyles.card(is_dark)["bgcolor"],
            actions=[
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Cambiar Tema",
                            icon=ThemeManager.get_theme_icon(is_dark),
                            on_click=lambda _: self.on_theme_change()
                        ),
                        ft.PopupMenuItem(
                            text="Gestionar Operadores",
                            icon=ft.Icons.MANAGE_ACCOUNTS,
                            on_click=lambda _: self.on_manage_operators()
                        ),
                    ]
                )
            ]
        )

    def update_theme(self):
        """Actualiza el tema del AppBar."""
        is_dark = self.app_state.is_dark_theme
        self.app_bar.title.style = TextStyles.subtitle(is_dark)
        self.app_bar.bgcolor = ContainerStyles.card(is_dark)["bgcolor"]
        theme_item = self.app_bar.actions[0].items[0]
        theme_item.icon = ThemeManager.get_theme_icon(is_dark)


class ReportDisplay:
    """Componente para mostrar el reporte generado."""

    def __init__(self, app_state: AppState):
        self.app_state = app_state
        self.text_widget = self._create_text_widget()
        self.container = self._create_container()

    def _create_text_widget(self) -> ft.Text:
        return ft.Text(
            spans=[],
            size=16,
            selectable=True,
            font_family="Segoe UI"
        )

    def _create_container(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [self.text_widget],
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            **ContainerStyles.card(self.app_state.is_dark_theme),
            expand=True
        )

    def update_report(self):
        """Actualiza el reporte mostrado."""
        reporte_texto = self.app_state.generar_reporte_actual()
        self.text_widget.spans = self._markdown_to_spans(reporte_texto)

    def _markdown_to_spans(self, texto: str) -> List[ft.TextSpan]:
        """Convierte markdown a TextSpans con el tema actual."""
        from models import ReportGenerator
        spans = ReportGenerator.markdown_a_textspan(texto)
        text_color = Colors.DARK["on_surface"] if self.app_state.is_dark_theme else Colors.LIGHT["on_surface"]
        for span in spans:
            if span.style:
                span.style.color = text_color
        return spans

    def update_theme(self):
        """Actualiza los colores según el tema."""
        container_style = ContainerStyles.card(self.app_state.is_dark_theme)
        for key, value in container_style.items():
            setattr(self.container, key, value)
        self.update_report()


class EjeCard(ft.Container):
    """Tarjeta que contiene los controles para un eje geográfico."""

    def __init__(self, app_state: AppState, eje_nombre: str, municipios: List[str], on_change: Callable):
        self.app_state = app_state
        self.eje_nombre = eje_nombre
        self.municipios = municipios
        self.on_change = on_change

        municipio_rows = [self._create_municipio_row(m) for m in self.municipios]
        content = ft.Column([
            ft.Text(f"📌 EJE {self.eje_nombre}", style=TextStyles.subtitle(self.app_state.is_dark_theme)),
            ft.Divider(),
            *municipio_rows
        ])

        super().__init__(
            content=content,
            **ContainerStyles.card(self.app_state.is_dark_theme)
        )

    def _create_municipio_row(self, municipio: str) -> ft.Row:
        """Crea una fila para un municipio con su selector de tiempo."""
        weather_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(
                    key=str(i),
                    text=f"{EMOJI_TIEMPO[i]} {nombre}"
                ) for i, nombre in enumerate(NOMBRES_TIEMPO)
            ],
            value="0",
            width=200,
            **InputStyles.dropdown(self.app_state.is_dark_theme),
        )

        time_field = ft.TextField(
            label="Hora (HH:MM)",
            width=120,
            visible=False,
            **InputStyles.textfield(self.app_state.is_dark_theme)
        )

        def on_dropdown_change(e):
            selected_index = int(e.control.value)
            selected_name = NOMBRES_TIEMPO[selected_index]
            is_event = "Evento" in selected_name
            time_field.visible = is_event
            self._update_municipio_state(municipio, selected_index, time_field.value)
            self.on_change()
            self.update()

        def on_time_change(e):
            selected_index = int(weather_dropdown.value)
            self._update_municipio_state(municipio, selected_index, e.control.value)
            self.on_change()

        weather_dropdown.on_change = on_dropdown_change
        time_field.on_change = on_time_change

        return ft.Row(
            controls=[
                ft.Text(municipio, expand=1, weight=ft.FontWeight.BOLD),
                weather_dropdown,
                time_field
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

    def _update_municipio_state(self, municipio: str, index: int, time_str: str):
        base_text = TIEMPO[index]
        if "evento" in base_text.lower() and time_str:
            estado_final = f"{time_str} {base_text}"
        else:
            estado_final = base_text
        self.app_state.actualizar_estado_municipio(municipio, estado_final)


class OperatorSelector(ft.Dropdown):
    """Selector de operador."""

    def __init__(self, app_state: AppState, on_change: Callable):
        self.app_state = app_state
        self.on_change_callback = on_change

        nombres = self.app_state.operador_manager.obtener_nombres()
        valor_inicial = nombres[self.app_state.indice_operador] if nombres else None

        super().__init__(
            label="Operador que reporta",
            options=[ft.dropdown.Option(nombre) for nombre in nombres],
            value=valor_inicial,
            on_change=self._on_dropdown_change,
            **InputStyles.dropdown(self.app_state.is_dark_theme),
            expand=True
        )

    def _on_dropdown_change(self, e):
        if e.control.value:
            self.app_state.cambiar_operador(e.control.value)
            self.on_change_callback()

    def refresh_options(self):
        """Actualiza las opciones del dropdown."""
        nombres = self.app_state.operador_manager.obtener_nombres()
        self.options = [ft.dropdown.Option(nombre) for nombre in nombres]
        if nombres and 0 <= self.app_state.indice_operador < len(nombres):
            self.value = nombres[self.app_state.indice_operador]
        else:
            self.value = None
        self.update()


class OperatorManagementDialog:
    """Clase para gestionar la creación y visualización del diálogo de operadores."""

    def __init__(self, app_state: AppState, operator_selector: OperatorSelector, page: ft.Page):
        self.app_state = app_state
        self.operator_selector = operator_selector
        self.page = page
        self.dialog = None

    def _create_form_fields(self):
        """Crea los campos del formulario."""
        style = InputStyles.textfield(self.app_state.is_dark_theme)
        self.nombre_field = ft.TextField(label="Nombre", width=300, hint_text="Nombre del operador", **style)
        self.cedula_field = ft.TextField(label="Cédula", width=300, hint_text="V-XX.XXX.XXX", **style)
        cargos = get_cargos(self.app_state.departamento)
        self.cargo_dropdown = ft.Dropdown(
            label="Cargo",
            width=300,
            options=[ft.dropdown.Option(cargo) for cargo in cargos],
            value=cargos[0] if cargos else None,
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )
        self.jerarquia_dropdown = ft.Dropdown(
            label="Jerarquía",
            width=300,
            options=[ft.dropdown.Option(j) for j in JERARQUIAS],
            value=JERARQUIAS[0],
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )
        self.eliminar_dropdown = ft.Dropdown(
            label="Eliminar operador",
            width=300,
            options=[ft.dropdown.Option(nombre) for nombre in self.app_state.operador_manager.obtener_nombres()],
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )

    def show(self, e=None):
        """Crea y muestra el diálogo."""
        self._create_form_fields()
        dialog_style = ContainerStyles.dialog(self.app_state.is_dark_theme)
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Gestión de Operadores", style=TextStyles.subtitle(self.app_state.is_dark_theme)),
            content=ft.Column([
                self.nombre_field, self.cedula_field, self.cargo_dropdown, self.jerarquia_dropdown,
                ft.Row([ft.ElevatedButton("Añadir", on_click=self._agregar_operador, style=ButtonStyles.primary())], alignment="center"),
                ft.Divider(),
                self.eliminar_dropdown,
                ft.Row([ft.ElevatedButton("Eliminar", on_click=self._eliminar_operador, style=ButtonStyles.danger())], alignment="center")
            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10, width=300, height=400),
            actions=[ft.ElevatedButton("Cerrar", on_click=self._cerrar_dialog, style=ButtonStyles.secondary(self.app_state.is_dark_theme))],
            actions_alignment="center",
            bgcolor=dialog_style.get("bgcolor"),
            shape=ft.RoundedRectangleBorder(radius=dialog_style.get("border_radius", 0))
        )
        self.page.open(self.dialog)

    def _agregar_operador(self, e):
        nombre = self.nombre_field.value.strip()
        cedula = self.cedula_field.value.strip()
        cargo = self.cargo_dropdown.value
        jerarquia = self.jerarquia_dropdown.value
        if self.app_state.operador_manager.agregar_operador(nombre, cargo, jerarquia, cedula):
            self.operator_selector.refresh_options()
            self._refresh_delete_dropdown()
            self.nombre_field.value = ""
            self.cedula_field.value = ""
            self._show_snackbar("Operador añadido", Colors.SUCCESS)
        else:
            self._show_snackbar("Error: Verifique los datos o si el operador ya existe", Colors.ERROR)
        self.page.update()

    def _eliminar_operador(self, e):
        nombre = self.eliminar_dropdown.value
        if nombre and self.app_state.operador_manager.eliminar_operador(nombre):
            self.operator_selector.refresh_options()
            self._refresh_delete_dropdown()
            self._show_snackbar("Operador eliminado", Colors.WARNING)
        else:
            self._show_snackbar("Error al eliminar operador", Colors.ERROR)
        self.page.update()

    def _refresh_delete_dropdown(self):
        nombres = self.app_state.operador_manager.obtener_nombres()
        self.eliminar_dropdown.options = [ft.dropdown.Option(nombre) for nombre in nombres]
        self.eliminar_dropdown.value = None
        self.dialog.content.update()

    def _cerrar_dialog(self, e):
        self.page.close(self.dialog)

    def _show_snackbar(self, mensaje: str, color):
        self.page.open(ft.SnackBar(ft.Text(mensaje, color=color)))


class ActionButtons(ft.FilledButton):
    """Botón de acción para copiar el reporte."""

    def __init__(self, app_state: AppState, page: ft.Page):
        self.app_state = app_state
        self.page = page
        super().__init__(
            text="Copiar al Portapapeles",
            icon=ft.Icons.CONTENT_COPY,
            on_click=self._copy_report,
            style=ButtonStyles.primary()
        )

    def _copy_report(self, e):
        reporte = self.app_state.generar_reporte_actual()
        self.page.set_clipboard(reporte)
        self.page.open(ft.SnackBar(ft.Text("¡Reporte copiado!", color=Colors.SUCCESS)))