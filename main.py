# main.py
"""
Aplicación principal para generar reportes meteorológicos.
Refactorizada con arquitectura limpia y componentes reutilizables.
"""
import flet as ft
from models import AppState
from ui_components import (
    ReportDisplay, WeatherSelector, OperatorSelector, 
    ActionButtons, SettingsDialog
)
from styles import ThemeManager, TextStyles, ContainerStyles, Colors
from config import WINDOW_CONFIG

class WeatherReportApp:
    """Aplicación principal de reportes meteorológicos."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.app_state = AppState()
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
        self.report_display = ReportDisplay(self.app_state)
        self.weather_selector = WeatherSelector(self.app_state, self._on_data_change)
        self.operator_selector = OperatorSelector(self.app_state, self._on_data_change)
        self.action_buttons = ActionButtons(self.app_state, self.operator_selector, self.page)
        self.settings_dialog = SettingsDialog(self.app_state, self.page)

    def _build_appbar(self) -> ft.AppBar:
        """Construye el AppBar de la aplicación."""
        is_dark = self.app_state.is_dark_theme
        appbar_color = ContainerStyles.card(is_dark)['bgcolor']

        return ft.AppBar(
            title=ft.Text("REPORTE DEL TIEMPO"),
            center_title=False,
            bgcolor=appbar_color,
            actions=[
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Cambiar Tema",
                            icon=ThemeManager.get_theme_icon(not is_dark),
                            on_click=self._toggle_theme_from_menu
                        ),
                        ft.PopupMenuItem(
                            text="Gestionar Operadores",
                            icon=ft.icons.PEOPLE_OUTLINE,
                            on_click=lambda e: self.action_buttons.operator_management.show()
                        ),
                        ft.PopupMenuItem(
                            text="Ajustes",
                            icon=ft.icons.SETTINGS_OUTLINED,
                            on_click=lambda e: self.settings_dialog.show()
                        ),
                    ]
                )
            ]
        )

    def _build_ui(self):
        """Construye la interfaz de usuario."""
        self.page.appbar = self._build_appbar()
        
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
        
        credits = ft.Text(
            "Creado por: Rubén Rojas",
            style=TextStyles.caption(self.app_state.is_dark_theme)
        )
        
        main_column = ft.Column([
            self.report_display.container,
            data_container,
            ft.Row([self.action_buttons.copy_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([credits], alignment=ft.MainAxisAlignment.CENTER)
        ], 
        expand=True, 
        alignment=ft.MainAxisAlignment.CENTER, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
        spacing=18)
        
        self.page.add(main_column)
        
        self.data_container = data_container
        self.credits = credits
    
    def _load_saved_theme(self):
        """Carga el tema guardado desde la configuración."""
        if self.app_state.is_dark_theme:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self._update_theme()

    def _toggle_theme_from_menu(self, e):
        """Cambia el tema desde el menú."""
        self.app_state.is_dark_theme = not self.app_state.is_dark_theme
        self._on_theme_change()

    def _on_theme_change(self):
        """Maneja el cambio de tema."""
        if self.app_state.is_dark_theme:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self.app_state.guardar_configuracion()
        
        self.page.bgcolor = ThemeManager.get_page_bgcolor(self.app_state.is_dark_theme)
        self._update_theme()
        self.page.update()
    
    def _update_theme(self):
        """Actualiza el tema de todos los componentes."""
        is_dark = self.app_state.is_dark_theme
        
        self.report_display.update_theme()
        self.weather_selector.update_theme()
        self.operator_selector.update_theme()
        self.action_buttons.update_theme()
        self.settings_dialog.update_theme()
        
        if self.page.appbar:
            self.page.appbar.bgcolor = ContainerStyles.card(is_dark)['bgcolor']
            theme_menu_item = self.page.appbar.actions[0].items[0]
            theme_menu_item.icon = ThemeManager.get_theme_icon(not is_dark)

        container_style = ContainerStyles.card(is_dark)
        for key, value in container_style.items():
            setattr(self.data_container, key, value)
        
        self.data_container.content.controls[0].style = TextStyles.subtitle(is_dark)
        self.credits.style = TextStyles.caption(is_dark)
        self.page.bgcolor = ThemeManager.get_page_bgcolor(is_dark)
    
    def _on_data_change(self):
        """Maneja los cambios en los datos (tiempo u operador)."""
        self.report_display.update_report()
        self.page.update()
    
    def _initial_update(self):
        """Realiza la actualización inicial de la interfaz."""
        self.report_display.update_report()
        self.page.update()

def main(page: ft.Page):
    """Función principal de la aplicación."""
    app = WeatherReportApp(page)

if __name__ == "__main__":
    ft.app(target=main)
