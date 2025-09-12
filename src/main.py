# main.py
"""
Aplicación principal para generar reportes meteorológicos.
Refactorizada con arquitectura limpia y componentes reutilizables.
"""
import flet as ft
import json
from models import AppState
from ui_components import (
    CustomAppBar, ReportDisplay, WeatherSelector, OperatorSelector,
    ActionButtons, SettingsDialog, OperatorManagementDialog
)
from styles import ThemeManager, TextStyles, ContainerStyles, Colors
from config import WINDOW_CONFIG, get_cargos, MUNICIPIOS, DEFAULT_OPERATORS

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
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def _create_components(self):
        """Crea los componentes de la interfaz."""
        self.weather_selector = WeatherSelector(self.app_state, self._on_data_change)
        self.operator_selector = OperatorSelector(self.app_state, self._on_data_change)
        self.settings_dialog = SettingsDialog(self.app_state, self.page, self._on_settings_save)

        self.app_bar = CustomAppBar(
            self.app_state,
            self._on_theme_toggle,
            self._show_operator_management_dialog,
            self.settings_dialog.show
        )
        self.page.appbar = self.app_bar.app_bar

        self.report_display = ReportDisplay(self.app_state)
        self.action_buttons = ActionButtons(self.app_state, self.operator_selector, self.page)

    def _build_ui(self):
        """Construye la interfaz de usuario."""
        data_container = ft.Container(
            ft.Column([
                ft.Text("Datos del reporte", style=TextStyles.subtitle(self.app_state.is_dark_theme)),
                self.weather_selector.dropdown,
                self.operator_selector.dropdown,
            ], alignment="center", horizontal_alignment="center", spacing=12),
            **ContainerStyles.card(self.app_state.is_dark_theme),
            width=500,
            alignment=ft.alignment.center
        )

        credits = ft.Text("Creado por: Rubén Rojas", style=TextStyles.caption(self.app_state.is_dark_theme))

        main_column = ft.Column([
            self.report_display.container,
            data_container,
            ft.Row([self.action_buttons.copy_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([credits], alignment=ft.MainAxisAlignment.CENTER)
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=18,
        scroll=ft.ScrollMode.ADAPTIVE)

        self.page.add(main_column)

        self.data_container = data_container
        self.credits = credits

    def _load_saved_theme(self):
        """Carga el tema guardado en el almacenamiento del cliente."""
        saved_theme = self.page.client_storage.get("theme")
        if saved_theme == "dark":
            self.app_state.is_dark_theme = True
        else:
            self.app_state.is_dark_theme = False

        self._apply_theme()

    def _on_theme_toggle(self):
        """Cambia el tema de la aplicación."""
        self.app_state.is_dark_theme = not self.app_state.is_dark_theme
        theme_value = "dark" if self.app_state.is_dark_theme else "light"
        self.page.client_storage.set("theme", theme_value)
        self._apply_theme()
        self.page.update()

    def _apply_theme(self):
        """Aplica el tema actual a todos los componentes."""
        self.page.theme_mode = ft.ThemeMode.DARK if self.app_state.is_dark_theme else ft.ThemeMode.LIGHT
        self.page.bgcolor = ThemeManager.get_page_bgcolor(self.app_state.is_dark_theme)

        self._update_themed_components()

    def _update_themed_components(self):
        """Actualiza el tema de todos los componentes personalizados."""
        if hasattr(self, 'app_bar'):
            self.app_bar.update_theme()
        self.report_display.update_theme()
        self.weather_selector.update_theme()
        self.operator_selector.update_theme()
        self.action_buttons.update_theme()
        self.settings_dialog.update_theme()

        container_style = ContainerStyles.card(self.app_state.is_dark_theme)
        for key, value in container_style.items():
            setattr(self.data_container, key, value)

        self.data_container.content.controls[0].style = TextStyles.subtitle(self.app_state.is_dark_theme)
        self.credits.style = TextStyles.caption(self.app_state.is_dark_theme)

    def _on_data_change(self, e=None):
        """Maneja los cambios en los datos (tiempo u operador)."""
        self.report_display.update_report()
        self.page.update()

    def _on_settings_save(self):
        """Se ejecuta cuando se guardan los ajustes."""
        self.report_display.update_report()
        self.page.update()

    def _show_operator_management_dialog(self, e=None):
        """Crea y muestra un nuevo diálogo de gestión de operadores."""
        dialog = OperatorManagementDialog(
            app_state=self.app_state,
            operator_selector=self.operator_selector,
            page=self.page
        )
        dialog.show()

    def _initial_update(self):
        """Realiza la actualización inicial de la interfaz."""
        self._on_data_change()

def main(page: ft.Page):
    """Función principal de la aplicación."""

    # Inicialización de datos por defecto si no existen
    if not page.client_storage.contains_key("operators"):
        page.client_storage.set("operators", json.dumps(DEFAULT_OPERATORS))

    if not page.client_storage.contains_key("municipalities"):
        page.client_storage.set("municipalities", json.dumps(MUNICIPIOS))

    app = WeatherReportApp(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
