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
        # self.theme_button = ThemeToggleButton(self.app_state, self._on_theme_change)
        self.report_display = ReportDisplay(self.app_state)
        self.weather_selector = WeatherSelector(self.app_state, self._on_data_change)
        self.operator_selector = OperatorSelector(self.app_state, self._on_data_change)
        self.action_buttons = ActionButtons(self.app_state, self.operator_selector, self.page)

    def _build_ui(self):
        """Construye la interfaz de usuario."""
        # Contenedor de datos del reporte
        data_container = ft.Container(
            ft.Column([
                ft.Text(
                    "Datos del reporte",
                    style=TextStyles.subtitle(self.app_state.is_dark_theme)
                ),
                self.weather_selector.dropdown,
                self.operator_selector.dropdown,
                self.action_buttons.manage_button
            ], alignment="center", horizontal_alignment="center", spacing=12),
            **ContainerStyles.card(self.app_state.is_dark_theme),
            width=500,
            alignment=ft.alignment.center
        )
        
        # Créditos
        credits = ft.Text(
            "Creado por: Rubén Rojas",
            style=TextStyles.caption(self.app_state.is_dark_theme)
        )
        
        # Layout principal
        main_column = ft.Column([
            # Botón de tema en la esquina superior derecha
            ft.Row([self.theme_button.button], alignment=ft.MainAxisAlignment.END),

            # Contenedor del reporte
            self.report_display.container,

            # Contenedor de datos
            data_container,

            # Botón de copiar
            ft.Row([self.action_buttons.copy_button], alignment=ft.MainAxisAlignment.CENTER),

            # Créditos
            ft.Row([credits], alignment=ft.MainAxisAlignment.CENTER)
        ], 
        expand=True, 
        alignment=ft.MainAxisAlignment.CENTER, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
        spacing=18)
        
        self.page.add(main_column)
        
        # Guardar referencia al contenedor de datos para actualizar tema
        self.data_container = data_container
        self.credits = credits
    
    def _load_saved_theme(self):
        """Carga el tema guardado en el almacenamiento del cliente."""
        saved_theme = self.page.client_storage.get("theme")
        if saved_theme == "dark":
            self.app_state.is_dark_theme = True
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.app_state.is_dark_theme = False
            self.page.theme_mode = ft.ThemeMode.LIGHT

        self._update_theme()

    def _on_theme_change(self):
        """Maneja el cambio de tema."""
        # Cambiar modo de tema de la página
        if self.app_state.is_dark_theme:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # Guardar preferencia
        theme_value = "dark" if self.app_state.is_dark_theme else "light"
        self.page.client_storage.set("theme", theme_value)
        
        # Actualizar colores de fondo
        self.page.bgcolor = ThemeManager.get_page_bgcolor(self.app_state.is_dark_theme)

        # Actualizar tema de todos los componentes
        self._update_theme()

        # Actualizar página
        self.page.update()
    
    def _update_theme(self):
        """Actualiza el tema de todos los componentes."""
        # Actualizar componentes
        self.report_display.update_theme()
        self.weather_selector.update_theme()
        self.operator_selector.update_theme()
        self.action_buttons.update_theme()
        
        # Actualizar contenedor de datos
        container_style = ContainerStyles.card(self.app_state.is_dark_theme)
        for key, value in container_style.items():
            setattr(self.data_container, key, value)
        
        # Actualizar título del contenedor de datos
        self.data_container.content.controls[0].style = TextStyles.subtitle(self.app_state.is_dark_theme)

        # Actualizar créditos
        self.credits.style = TextStyles.caption(self.app_state.is_dark_theme)

        # Actualizar fondo de la página
        self.page.bgcolor = ThemeManager.get_page_bgcolor(self.app_state.is_dark_theme)
    
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