# main.py
"""
Aplicación principal para generar reportes meteorológicos estadales.
"""
import flet as ft
import json
from models import AppState
from ui_components import (
    CustomAppBar, OperatorSelector, ActionButtons,
    OperatorManagementDialog, EjeCard
)
from styles import ThemeManager, TextStyles, ContainerStyles, Colors
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

    def _setup_page(self):
        """Configura las propiedades básicas de la página."""
        self.page.title = WINDOW_CONFIG["title"]
        self.page.window.width = WINDOW_CONFIG["width"]
        self.page.window.height = WINDOW_CONFIG["height"]
        self.page.window.min_width = WINDOW_CONFIG["min_width"]
        self.page.window.min_height = WINDOW_CONFIG["min_height"]
        self.page.window.resizable = WINDOW_CONFIG["resizable"]
        self.page.window.maximizable = WINDOW_CONFIG["maximizable"]
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def _create_components(self):
        """Crea los componentes de la interfaz."""
        self.operator_selector = OperatorSelector(self.app_state, self._on_data_change)
        self.operator_management_dialog = OperatorManagementDialog(self.app_state, self.operator_selector, self.page)
        self.app_bar = CustomAppBar(self.app_state, self._on_theme_toggle, self.operator_management_dialog.show)
        self.page.appbar = self.app_bar.app_bar
        self.action_buttons = ActionButtons(self.app_state, self.page, on_copy=self._handle_copy_report)
        self.eje_cards = [EjeCard(self.app_state, nombre, municipios) for nombre, municipios in EJES.items()]

    def _build_ui(self):
        """Construye la interfaz de usuario."""
        ejes_row = ft.Row(
            controls=self.eje_cards,
            spacing=10,
            expand=True
        )
        controles_card = ft.Container(
            content=ft.Column(
                [self.operator_selector, self.action_buttons],
                spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True
            ),
            **ContainerStyles.card(self.app_state.is_dark_theme),
        )
        credits = ft.Text("Creado por: Rubén Rojas", style=TextStyles.caption(self.app_state.is_dark_theme))
        main_column = ft.Column(
            [ejes_row, controles_card, ft.Row([credits], alignment=ft.MainAxisAlignment.CENTER)],
            expand=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.page.add(main_column)

    def _handle_copy_report(self):
        """Valida todas las entradas y copia el reporte si son válidas."""
        all_valid = True
        for card in self.eje_cards:
            if not card.validate():
                all_valid = False

        if all_valid:
            reporte = self.app_state.generar_reporte_actual()
            self.page.set_clipboard(reporte)
            self.page.open(ft.SnackBar(ft.Text("¡Reporte copiado!", color=Colors.SUCCESS)))
        else:
            self.page.open(ft.SnackBar(ft.Text("Por favor, complete todos los campos requeridos.", color=Colors.ERROR)))
        self.page.update()

    def _load_saved_theme(self):
        self.app_state.is_dark_theme = self.page.client_storage.get("theme") == "dark"
        self._apply_theme()

    def _on_theme_toggle(self, e=None):
        self.app_state.is_dark_theme = not self.app_state.is_dark_theme
        self.page.client_storage.set("theme", "dark" if self.app_state.is_dark_theme else "light")
        self._apply_theme()

    def _apply_theme(self):
        self.page.theme_mode = ft.ThemeMode.DARK if self.app_state.is_dark_theme else ft.ThemeMode.LIGHT
        self.page.bgcolor = ThemeManager.get_page_bgcolor(self.app_state.is_dark_theme)
        # Reconstruir la UI para aplicar temas a los componentes dinámicos
        self.page.controls.clear()
        self._create_components()
        self._build_ui()
        self.page.update()

    def _on_data_change(self, e=None):
        """Callback vacío, la lógica de actualización está en los componentes."""
        pass

def main(page: ft.Page):
    """Función principal de la aplicación."""
    if not page.client_storage.contains_key("operators"):
        page.client_storage.set("operators", json.dumps(DEFAULT_OPERATORS))

    for key in ["municipalities", "municipio", "departamento"]:
        if page.client_storage.contains_key(key):
            page.client_storage.remove(key)

    app = WeatherReportApp(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
