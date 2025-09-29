# main.py
"""
Aplicación principal para generar reportes meteorológicos estadales.
"""
import flet as ft
import json
from models import AppState
from ui_components import (
    CustomAppBar, OperatorSelector,
    OperatorManagementDialog, EjeCard
)
from styles import ThemeManager, TextStyles, ContainerStyles, Colors, ButtonStyles
from config import WINDOW_CONFIG, DEFAULT_OPERATORS, EJES
from typing import Callable

class ActionsCard(ft.Container):
    """Tarjeta de acciones con el selector de operador y el botón de copiar."""
    def __init__(self, app_state: AppState, operator_selector: OperatorSelector, on_copy: Callable):
        super().__init__()
        self.app_state = app_state
        self.operator_selector = operator_selector
        self.on_copy = on_copy
        self._build()
        self.update_theme()

    def _build(self):
        """Construye el contenido de la tarjeta."""
        self.copy_button = ft.FilledButton(
            "Copiar Reporte", icon=ft.Icons.CONTENT_COPY, on_click=lambda _: self.on_copy(), expand=True
        )
        self.operator_selector.label = "Operador que reporta"
        self.operator_selector.hint_text = ""
        self.title = ft.Text("Acciones y Reporte")
        self.content = ft.Column(
            [self.title, ft.Divider(), self.operator_selector, self.copy_button], spacing=10
        )

    def update_theme(self):
        """Actualiza el tema de la tarjeta."""
        is_dark = self.app_state.is_dark_theme
        card_style = ContainerStyles.card(is_dark)
        self.padding = card_style.get("padding")
        self.bgcolor = card_style.get("bgcolor")
        self.border_radius = card_style.get("border_radius")
        self.shadow = card_style.get("shadow")
        self.title.style = TextStyles.subtitle(is_dark)
        self.operator_selector.update_theme()
        self.copy_button.style = ButtonStyles.primary()


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
        self.page.scroll = ft.ScrollMode.ADAPTIVE

    def _create_components(self):
        """Crea los componentes de la interfaz."""
        self.operator_selector = OperatorSelector(self.app_state, self._on_data_change)
        self.operator_management_dialog = OperatorManagementDialog(self.app_state, self.operator_selector, self.page)
        self.app_bar = CustomAppBar(
            self.app_state,
            self._on_theme_toggle,
            self.operator_management_dialog.show
        )
        self.page.appbar = self.app_bar.app_bar

        self.eje_cards = [
            ft.Container(
                content=EjeCard(self.app_state, nombre, municipios),
                col={"sm": 12, "md": 6, "xl": 3}
            )
            for nombre, municipios in EJES.items()
        ]

        actions_card = ft.Container(
            content=ActionsCard(self.app_state, self.operator_selector, self._handle_copy_report),
            col={"sm": 12, "md": 6, "xl": 3}
        )

        self.all_cards = self.eje_cards + [actions_card]

    def _build_ui(self):
        """Construye la interfaz de usuario."""
        main_view = ft.ResponsiveRow(
            controls=self.all_cards,
            spacing=10,
            run_spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START
        )
        self.page.add(main_view)

    def update_theme(self):
        """Actualiza el tema de toda la aplicación."""
        self.app_bar.update_theme()
        for card_container in self.all_cards:
            # Asumiendo que el contenido de cada contenedor (EjeCard, ActionsCard) tiene un método update_theme
            if hasattr(card_container.content, 'update_theme'):
                card_container.content.update_theme()
        self.page.update()

    def _handle_copy_report(self):
        """Valida todas las entradas y copia el reporte si son válidas."""
        all_valid = True
        for container in self.eje_cards:
            eje_card = container.content
            if not eje_card.validate():
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
        """Aplica el tema actual a la página y a todos los componentes."""
        is_dark = self.app_state.is_dark_theme
        self.page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        self.page.bgcolor = ThemeManager.get_page_bgcolor(is_dark)

        # Llama incondicionalmente a update_theme.
        # Es seguro porque _apply_theme siempre se llama después de que los componentes han sido creados.
        self.update_theme()

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
