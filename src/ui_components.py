# ui_components.py
"""
Componentes de interfaz de usuario reutilizables.
"""
import flet as ft
import json
from typing import Callable, Optional, List
from models import AppState, Operador, ReportGenerator
from styles import (
    TextStyles, ButtonStyles, ContainerStyles, InputStyles, 
    Colors, ThemeManager
)
from config import EMOJI_TIEMPO, NOMBRES_TIEMPO, get_cargos, JERARQUIAS, WINDOW_CONFIG

class CustomAppBar:
    """AppBar personalizada con título y menú de opciones."""

    def __init__(self, app_state: AppState, on_theme_change: Callable, on_manage_operators: Callable, on_show_settings: Callable):
        self.app_state = app_state
        self.on_theme_change = on_theme_change
        self.on_manage_operators = on_manage_operators
        self.on_show_settings = on_show_settings
        self.app_bar = self._create_app_bar()

    def _create_app_bar(self) -> ft.AppBar:
        """Crea el widget AppBar."""
        is_dark = self.app_state.is_dark_theme

        return ft.AppBar(
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
                        ft.PopupMenuItem(
                            text="Ajustes Generales",
                            icon=ft.Icons.SETTINGS,
                            on_click=lambda _: self.on_show_settings()
                        )
                    ]
                )
            ]
        )

    def update_theme(self):
        """Actualiza el tema del AppBar."""
        is_dark = self.app_state.is_dark_theme

        # Actualizar título
        self.app_bar.title.style = TextStyles.subtitle(is_dark)

        # Actualizar color de fondo
        self.app_bar.bgcolor = ContainerStyles.card(is_dark)["bgcolor"]

        # Actualizar ícono del tema en el menú
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
            size=17,
            color=Colors.DARK["on_surface"] if self.app_state.is_dark_theme else Colors.LIGHT["on_surface"],
            font_family="Segoe UI",
            selectable=False
        )
    
    def _create_container(self) -> ft.Container:
        return ft.Container(
            ft.Column([
                self.text_widget
            ], alignment="center", horizontal_alignment="center", spacing=12),
            **ContainerStyles.card(self.app_state.is_dark_theme),
            alignment=ft.alignment.center
        )
    
    def update_report(self):
        """Actualiza el reporte mostrado."""
        reporte_texto = self.app_state.generar_reporte_actual()
        self.text_widget.spans = self._markdown_to_spans(reporte_texto)
    
    def _markdown_to_spans(self, texto: str) -> List[ft.TextSpan]:
        """Convierte markdown a TextSpans con el tema actual."""
        spans = ReportGenerator.markdown_a_textspan(texto)
        
        # Actualizar colores según el tema actual
        text_color = Colors.DARK["on_surface"] if self.app_state.is_dark_theme else Colors.LIGHT["on_surface"]
        
        for span in spans:
            if span.style:
                span.style.color = text_color
        
        return spans
    
    def update_theme(self):
        """Actualiza los colores según el tema."""
        self.text_widget.color = Colors.DARK["on_surface"] if self.app_state.is_dark_theme else Colors.LIGHT["on_surface"]
        
        # Actualizar container
        container_style = ContainerStyles.card(self.app_state.is_dark_theme)
        for key, value in container_style.items():
            setattr(self.container, key, value)
        
        # Actualizar spans del reporte
        self.update_report()

class WeatherSelector:
    """Selector de estado del tiempo."""
    
    def __init__(self, app_state: AppState, on_change: Callable):
        self.app_state = app_state
        self.on_change = on_change
        self.dropdown = self._create_dropdown()
    
    def _create_dropdown(self) -> ft.Dropdown:
        return ft.Dropdown(
            width=380,
            options=[
                ft.dropdown.Option(
                    key=str(i),
                    text=f"{EMOJI_TIEMPO[i]}  {nombre}"
                ) for i, nombre in enumerate(NOMBRES_TIEMPO)
            ],
            value=str(self.app_state.indice_tiempo),
            on_change=self._on_dropdown_change,
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )
    
    def _on_dropdown_change(self, e):
        try:
            indice = int(e.control.value)
            self.app_state.cambiar_tiempo(indice)
            self.on_change()
        except (ValueError, TypeError):
            pass
    
    def update_theme(self):
        """Actualiza el estilo según el tema."""
        style = InputStyles.dropdown(self.app_state.is_dark_theme)
        for key, value in style.items():
            setattr(self.dropdown, key, value)

class OperatorSelector:
    """Selector de operador."""
    
    def __init__(self, app_state: AppState, on_change: Callable):
        self.app_state = app_state
        self.on_change = on_change
        self.dropdown = self._create_dropdown()
    
    def _create_dropdown(self) -> ft.Dropdown:
        nombres = self.app_state.operador_manager.obtener_nombres()
        valor_inicial = nombres[self.app_state.indice_operador] if nombres else None
        
        return ft.Dropdown(
            width=380,
            options=[ft.dropdown.Option(nombre) for nombre in nombres],
            value=valor_inicial,
            on_change=self._on_dropdown_change,
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )
    
    def _on_dropdown_change(self, e):
        if e.control.value:
            self.app_state.cambiar_operador(e.control.value)
            self.on_change()
    
    def refresh_options(self):
        """Actualiza las opciones del dropdown."""
        nombres = self.app_state.operador_manager.obtener_nombres()
        self.dropdown.options = [ft.dropdown.Option(nombre) for nombre in nombres]
        
        # Actualizar valor seleccionado
        if nombres and 0 <= self.app_state.indice_operador < len(nombres):
            self.dropdown.value = nombres[self.app_state.indice_operador]
        else:
            self.dropdown.value = None
    
    def update_theme(self):
        """Actualiza el estilo según el tema."""
        style = InputStyles.dropdown(self.app_state.is_dark_theme)
        for key, value in style.items():
            setattr(self.dropdown, key, value)

class OperatorManagementDialog:
    """Diálogo para gestionar operadores."""
    
    def __init__(self, app_state: AppState, operator_selector: OperatorSelector, page: ft.Page):
        self.app_state = app_state
        self.operator_selector = operator_selector
        self.page = page
        self.dialog = None
        self._create_form_fields()
    
    def _create_form_fields(self):
        """Crea los campos del formulario."""
        style = InputStyles.textfield(self.app_state.is_dark_theme)
        
        self.nombre_field = ft.TextField(
            label="Nombre",
            width=300,
            hint_text="Nombre del operador",
            **style
        )
        
        self.cedula_field = ft.TextField(
            label="Cédula",
            width=300,
            hint_text="Cédula",
            **style
        )
        
        cargos = get_cargos(self.app_state.departamento)
        self.cargo_dropdown = ft.Dropdown(
            label="Cargo",
            width=300,
            options=[ft.dropdown.Option(cargo) for cargo in cargos],
            value=cargos[0],
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
            options=[
                ft.dropdown.Option(nombre) 
                for nombre in self.app_state.operador_manager.obtener_nombres()
            ],
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )

    def update_theme(self):
        """Actualiza los estilos de los componentes del diálogo."""
        is_dark = self.app_state.is_dark_theme

        # Actualizar TextFields
        tf_style = InputStyles.textfield(is_dark)
        for field in [self.nombre_field, self.cedula_field]:
            for key, value in tf_style.items():
                setattr(field, key, value)

        # Actualizar Dropdowns
        dd_style = InputStyles.dropdown(is_dark)
        for dropdown in [self.cargo_dropdown, self.jerarquia_dropdown, self.eliminar_dropdown]:
            for key, value in dd_style.items():
                setattr(dropdown, key, value)

        # Si el diálogo está abierto, actualizar sus propiedades
        if self.dialog:
            # Actualizar título
            self.dialog.title.style = TextStyles.subtitle(is_dark)

            # Actualizar botón de cerrar
            self.dialog.actions[0].style = ButtonStyles.secondary(is_dark)

            # Actualizar propiedades del diálogo
            dialog_style = ContainerStyles.dialog(is_dark)
            self.dialog.bgcolor = dialog_style.get("bgcolor")
            self.dialog.shape = ft.RoundedRectangleBorder(radius=dialog_style.get("border_radius", 0))

    def show(self):
        """Muestra el diálogo."""
        # Actualiza las opciones de cargo dinámicamente cada vez que se muestra el diálogo.
        # Esto asegura que si el departamento cambió en los Ajustes, se refleje aquí.
        cargos = get_cargos(self.app_state.departamento)
        self.cargo_dropdown.options.clear()
        self.cargo_dropdown.options.extend([ft.dropdown.Option(cargo) for cargo in cargos])
        # Asegurarse de que el valor seleccionado sea válido
        if self.cargo_dropdown.value not in cargos:
            self.cargo_dropdown.value = cargos[0] if cargos else None

        # Actualizar tema antes de mostrar
        self.update_theme()

        dialog_style = ContainerStyles.dialog(self.app_state.is_dark_theme)
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Gestión de Operadores",
                style=TextStyles.subtitle(self.app_state.is_dark_theme)
            ),
            content=ft.Column([
                self.nombre_field,
                self.cedula_field,
                self.cargo_dropdown,
                self.jerarquia_dropdown,
                ft.Row([
                    ft.ElevatedButton(
                        "Añadir",
                        on_click=self._agregar_operador,
                        style=ButtonStyles.primary()
                    )
                ], alignment="center"),
                ft.Divider(),
                self.eliminar_dropdown,
                ft.Row([
                    ft.ElevatedButton(
                        "Eliminar",
                        on_click=self._eliminar_operador,
                        style=ButtonStyles.danger()
                    )
                ], alignment="center")
            ], tight=True, width=300, alignment="center", horizontal_alignment="center"),
            actions=[
                ft.ElevatedButton(
                    "Cerrar",
                    on_click=self._cerrar_dialog,
                    style=ButtonStyles.secondary(self.app_state.is_dark_theme)
                )
            ],
            actions_alignment="center",
            bgcolor=dialog_style.get("bgcolor"),
            shape=ft.RoundedRectangleBorder(radius=dialog_style.get("border_radius", 0))
        )
        
        self.page.open(self.dialog)
    
    def _agregar_operador(self, e):
        """Agrega un nuevo operador."""
        nombre = self.nombre_field.value.strip() if self.nombre_field.value else ""
        cedula = self.cedula_field.value.strip() if self.cedula_field.value else ""
        cargo = self.cargo_dropdown.value
        jerarquia = self.jerarquia_dropdown.value
        
        if self.app_state.operador_manager.agregar_operador(nombre, cargo, jerarquia, cedula):
            # Actualizar selector
            self.operator_selector.refresh_options()
            self.app_state.cambiar_operador(nombre)
            
            # Actualizar dropdown de eliminación
            self._refresh_delete_dropdown()
            
            # Limpiar campos
            self.nombre_field.value = ""
            self.cedula_field.value = ""
            
            # Mostrar mensaje
            self._show_snackbar("Operador añadido", Colors.SUCCESS)
        else:
            self._show_snackbar("Error: Verifique los datos o si el operador ya existe", Colors.ERROR)
    
    def _eliminar_operador(self, e):
        """Elimina un operador."""
        nombre_seleccionado = self.eliminar_dropdown.value
        if nombre_seleccionado and self.app_state.operador_manager.eliminar_operador(nombre_seleccionado):
            # Actualizar selector
            self.operator_selector.refresh_options()
            
            # Ajustar índice si es necesario
            if self.app_state.operador_manager.cantidad == 0:
                self.app_state.indice_operador = 0
            elif self.app_state.indice_operador >= self.app_state.operador_manager.cantidad:
                self.app_state.indice_operador = self.app_state.operador_manager.cantidad - 1
            
            # Actualizar dropdown de eliminación
            self._refresh_delete_dropdown()
            
            # Mostrar mensaje
            self._show_snackbar("Operador eliminado", Colors.WARNING)
        else:
            self._show_snackbar("Error al eliminar operador", Colors.ERROR)
    
    def _refresh_delete_dropdown(self):
        """Actualiza el dropdown de eliminación."""
        nombres = self.app_state.operador_manager.obtener_nombres()
        self.eliminar_dropdown.options = [ft.dropdown.Option(nombre) for nombre in nombres]
        self.eliminar_dropdown.value = None
        
        # Aplicar estilos actualizados
        dropdown_style = InputStyles.dropdown(self.app_state.is_dark_theme)
        for key, value in dropdown_style.items():
            setattr(self.eliminar_dropdown, key, value)
    
    def _cerrar_dialog(self, e):
        """Cierra el diálogo."""
        self.page.close(self.dialog)
    
    def _show_snackbar(self, mensaje: str, color):
        """Muestra un snackbar con un mensaje."""
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje, color=color))
        self.page.snack_bar.open = True
        self.page.update()

class SettingsDialog:
    """Diálogo para configurar el departamento y municipio."""

    def __init__(self, app_state: AppState, page: ft.Page, on_save: Callable):
        self.app_state = app_state
        self.page = page
        self.on_save = on_save
        self.dialog = None
        self.municipalities = self._load_municipalities()
        self._create_form_fields()

    def _load_municipalities(self) -> List[str]:
        """Carga la lista de municipios desde el archivo JSON."""
        try:
            with open("storage/municipios.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error al cargar municipios.json: {e}")
            return ["Guanta"] # Valor de respaldo

    def _create_form_fields(self):
        """Crea los campos del formulario de ajustes."""
        self.departamento_field = ft.TextField(
            label="Departamento",
            value=self.app_state.departamento,
            width=300,
            **InputStyles.textfield(self.app_state.is_dark_theme)
        )
        self.municipio_dropdown = ft.Dropdown(
            label="Municipio",
            options=[ft.dropdown.Option(m) for m in self.municipalities],
            value=self.app_state.municipio,
            width=300,
            **InputStyles.dropdown(self.app_state.is_dark_theme)
        )

    def update_theme(self):
        """Actualiza los estilos de los componentes del diálogo."""
        is_dark = self.app_state.is_dark_theme

        # Actualizar TextField
        tf_style = InputStyles.textfield(is_dark)
        for key, value in tf_style.items():
            setattr(self.departamento_field, key, value)

        # Actualizar Dropdown
        dd_style = InputStyles.dropdown(is_dark)
        for key, value in dd_style.items():
            setattr(self.municipio_dropdown, key, value)

        if self.dialog:
            self.dialog.title.style = TextStyles.subtitle(is_dark)
            self.dialog.actions[0].style = ButtonStyles.primary()
            self.dialog.actions[1].style = ButtonStyles.secondary(is_dark)
            dialog_style = ContainerStyles.dialog(is_dark)
            self.dialog.bgcolor = dialog_style.get("bgcolor")
            self.dialog.shape = ft.RoundedRectangleBorder(radius=dialog_style.get("border_radius", 0))

    def show(self):
        """Muestra el diálogo de ajustes."""
        self.update_theme()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Ajustes Generales"),
            content=ft.Column([
                self.departamento_field,
                self.municipio_dropdown
            ], tight=True, width=300, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.ElevatedButton("Guardar", on_click=self._save_settings),
                ft.ElevatedButton("Cerrar", on_click=self._close_dialog)
            ],
            actions_alignment="center"
        )

        # Aplicar estilos al abrir
        self.update_theme()

        self.page.open(self.dialog)

    def _save_settings(self, e):
        """Guarda los ajustes y cierra el diálogo."""
        self.app_state.departamento = self.departamento_field.value or "PROTECCIÓN CIVIL"
        self.app_state.municipio = self.municipio_dropdown.value or "Guanta"
        self.app_state.guardar_configuracion()

        # Llama al callback para actualizar la UI principal
        self.on_save()

        self._show_snackbar("Ajustes guardados", Colors.SUCCESS)
        self._close_dialog(e)

    def _close_dialog(self, e):
        """Cierra el diálogo."""
        self.page.close(self.dialog)

    def _show_snackbar(self, mensaje: str, color):
        """Muestra un snackbar con un mensaje."""
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje, color=color))
        self.page.snack_bar.open = True
        self.page.update()

class ActionButtons:
    """Botones de acción de la aplicación."""
    
    def __init__(self, app_state: AppState, operator_selector: OperatorSelector, page: ft.Page):
        self.app_state = app_state
        self.page = page
        self.operator_management = OperatorManagementDialog(app_state, operator_selector, page)
        self.copy_button = self._create_copy_button()
        self.manage_button = self._create_manage_button()

    def _create_manage_button(self) -> ft.ElevatedButton:
        """Crea el botón para gestionar operadores."""
        return ft.ElevatedButton(
            "Gestionar Operadores",
            icon=ft.Icons.MANAGE_ACCOUNTS,
            on_click=lambda _: self.operator_management.show(),
            style=ButtonStyles.secondary(self.app_state.is_dark_theme)
        )

    def _create_copy_button(self) -> ft.FilledButton:
        return ft.FilledButton(
            "Copiar al Portapapeles",
            icon=ft.Icons.CONTENT_COPY,
            on_click=self._copy_report,
            style=ButtonStyles.primary()
        )
    
    def _copy_report(self, e):
        """Copia el reporte al portapapeles."""
        reporte = self.app_state.generar_reporte_actual()
        self.page.set_clipboard(reporte)
        
        snackbar = ft.SnackBar(ft.Text("¡Reporte copiado!", color=Colors.SUCCESS))
        self.page.open(snackbar)
        self.page.update()
    
    def update_theme(self):
        """Actualiza los estilos según el tema."""
        self.operator_management.update_theme()
        self.manage_button.style = ButtonStyles.secondary(self.app_state.is_dark_theme)