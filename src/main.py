# main.py
"""
Aplicación principal para generar reportes meteorológicos estadales.
"""
import flet as ft
import json
from models import AppState
from ui_components import (
    CustomAppBar, ReportDisplay, OperatorSelector, ActionButtons,
    OperatorManagementDialog, EjeCard
)
from styles import ThemeManager, TextStyles
from config import WINDOW_CONFIG, DEFAULT_OPERATORS, EJES


class WeatherReportApp:
    """Aplicación principal de reportes meteorológicos."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.app_state = AppState(page=page)
        self._setup_page()
        self._create_components()
        self._build_ui()
        self._load_saved_theme()
        self._initial_update()

    def _setup_page(self):
        """Configura las propiedades básicas de la página."""
        self.page.title = WINDOW_CONFIG["title"]
        self.page.window.width = WINDOW_CONFIG["width"]
        self.page.window.height = WINDOW_CONFIG["height"]
        self.page.window.resizable = WINDOW_CONFIG["resizable"]
        self.page.window.maximizable = WINDOW_CONFIG["maximizable"]
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def _create_components(self):
        """Crea los componentes de la interfaz."""
        self.operator_selector = OperatorSelector(self.app_state, self._on_data_change)
        self.operator_management_dialog = OperatorManagementDialog(
            self.app_state, self.operator_selector, self.page
        )

        self.app_bar = CustomAppBar(
            self.app_state,
            self._on_theme_toggle,
            self.operator_management_dialog.show
        )
        self.page.appbar = self.app_bar.app_bar

        self.report_display = ReportDisplay(self.app_state)
        self.action_buttons = ActionButtons(self.app_state, self.page)

        # Crear tarjetas para cada eje
        self.eje_cards = [
            EjeCard(self.app_state, nombre, municipios, self._on_data_change)
            for nombre, municipios in EJES.items()
        ]

    def _build_ui(self):
        """Construye la interfaz de usuario."""
        controls_column = ft.Column(
            self.eje_cards,
            spacing=15,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

        left_panel = ft.Column(
            [
                controls_column,
                ft.Divider(),
                ft.Row([self.operator_selector], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.action_buttons], alignment=ft.MainAxisAlignment.CENTER),
            ],
            expand=1,
            spacing=15
        )

        right_panel = ft.Column(
            [self.report_display.container],
            expand=1
        )

        main_row = ft.Row(
            [
                ft.Container(
                    left_panel,
                    padding=ft.padding.only(top=10, left=10, right=10, bottom=20)
                ),
                ft.VerticalDivider(),
                ft.Container(
                    right_panel,
                    padding=ft.padding.only(top=10, right=10, bottom=20)
                )
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        self.page.add(main_row)

    def _load_saved_theme(self):
        """Carga el tema guardado."""
        saved_theme = self.page.client_storage.get("theme")
        self.app_state.is_dark_theme = saved_theme == "dark"
        self._apply_theme()

    def _on_theme_toggle(self, e=None):
        """Cambia el tema de la aplicación."""
        self.app_state.is_dark_theme = not self.app_state.is_dark_theme
        self.page.client_storage.set("theme", "dark" if self.app_state.is_dark_theme else "light")
        self._apply_theme()
        self.page.update()

    def _apply_theme(self):
        """Aplica el tema actual a todos los componentes."""
        self.page.theme_mode = ft.ThemeMode.DARK if self.app_state.is_dark_theme else ft.ThemeMode.LIGHT
        self.page.bgcolor = ThemeManager.get_page_bgcolor(self.app_state.is_dark_theme)
        # Reconstruir la UI para aplicar temas a los componentes dinámicos
        self.page.controls.clear()
        self._create_components()
        self._build_ui()
        self.page.update()
        self._initial_update()

    def _on_data_change(self, e=None):
        """Maneja los cambios en los datos."""
        self.report_display.update_report()
        self.page.update()

    def _initial_update(self):
        """Realiza la actualización inicial de la interfaz."""
        self._on_data_change()


def main(page: ft.Page):
    """Función principal de la aplicación."""
    if not page.client_storage.contains_key("operators"):
        page.client_storage.set("operators", json.dumps(DEFAULT_OPERATORS))

    # Eliminar configuraciones viejas si existen
    if page.client_storage.contains_key("municipalities"):
        page.client_storage.remove("municipalities")
    if page.client_storage.contains_key("municipio"):
        page.client_storage.remove("municipio")
    if page.client_storage.contains_key("departamento"):
        page.client_storage.remove("departamento")

    app = WeatherReportApp(page)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
