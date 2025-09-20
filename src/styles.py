# styles.py
"""
Estilos y temas de la aplicación.
"""
import flet as ft
from config import FONT_FAMILY, BORDER_RADIUS

class Colors:
    """Paleta de colores de la aplicación."""
    
    # Colores principales
    PRIMARY = "#005a9e"
    PRIMARY_LIGHT = "#0078d4"
    PRIMARY_DARK = "#004578"
    
    # Tema claro
    LIGHT = {
        "background": "#f3f3f3",
        "surface": "#f9f9f9",
        "surface_dialog": "#ffffff",
        "on_surface": "#202020",
        "border": "#e1e1e1",
        "text_secondary": "#616161"
    }
    
    # Tema oscuro
    DARK = {
        "background": "#1a1a1a",
        "surface": "#2d2d2d",
        "surface_dialog": "#3d3d3d",
        "on_surface": "#ffffff",
        "border": "#555555",
        "text_secondary": "#b0b0b0"
    }
    
    # Estados
    SUCCESS = ft.Colors.GREEN
    ERROR = ft.Colors.RED_400
    WARNING = ft.Colors.ORANGE

class Shadows:
    """Sombras predefinidas."""
    
    SMALL = ft.BoxShadow(
        blur_radius=8,
        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        offset=ft.Offset(0, 2)
    )
    
    MEDIUM = ft.BoxShadow(
        blur_radius=16,
        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        offset=ft.Offset(0, 4)
    )
    
    LARGE = ft.BoxShadow(
        blur_radius=24,
        color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
        offset=ft.Offset(0, 8)
    )

class TextStyles:
    """Estilos de texto predefinidos."""
    
    @staticmethod
    def title(is_dark_theme=False):
        return ft.TextStyle(
            size=32,
            weight=ft.FontWeight.W_700,
            color=Colors.DARK["on_surface"] if is_dark_theme else Colors.LIGHT["on_surface"],
            font_family=FONT_FAMILY
        )
    
    @staticmethod
    def subtitle(is_dark_theme=False):
        return ft.TextStyle(
            size=18,
            weight=ft.FontWeight.W_600,
            color=Colors.DARK["on_surface"] if is_dark_theme else Colors.LIGHT["on_surface"],
            font_family=FONT_FAMILY
        )
    
    @staticmethod
    def body(is_dark_theme=False):
        return ft.TextStyle(
            size=16,
            color=Colors.DARK["on_surface"] if is_dark_theme else Colors.LIGHT["on_surface"],
            font_family=FONT_FAMILY
        )
    
    @staticmethod
    def body_large(is_dark_theme=False):
        return ft.TextStyle(
            size=17,
            color=Colors.DARK["on_surface"] if is_dark_theme else Colors.LIGHT["on_surface"],
            font_family=FONT_FAMILY
        )
    
    @staticmethod
    def caption(is_dark_theme=False):
        return ft.TextStyle(
            size=13,
            italic=True,
            color=Colors.DARK["text_secondary"] if is_dark_theme else Colors.LIGHT["text_secondary"],
            font_family=FONT_FAMILY
        )

class ButtonStyles:
    """Estilos de botones predefinidos."""
    
    @staticmethod
    def primary():
        return ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS["control"]),
            bgcolor=Colors.PRIMARY,
            color=ft.Colors.WHITE,
            overlay_color=ft.Colors.with_opacity(0.08, Colors.PRIMARY),
            shadow_color=ft.Colors.with_opacity(0.15, Colors.PRIMARY),
            text_style=ft.TextStyle(font_family=FONT_FAMILY)
        )
    
    @staticmethod
    def secondary(is_dark_theme=False):
        return ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS["control"]),
            bgcolor=Colors.DARK["surface"] if is_dark_theme else Colors.LIGHT["surface"],
            color=Colors.PRIMARY,
            overlay_color=ft.Colors.with_opacity(0.08, Colors.PRIMARY),
            shadow_color=ft.Colors.with_opacity(0.10, Colors.PRIMARY),
            side=ft.BorderSide(1, Colors.PRIMARY),
            text_style=ft.TextStyle(font_family=FONT_FAMILY)
        )
    
    @staticmethod
    def danger():
        return ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS["control"]),
            bgcolor=Colors.ERROR,
            color=ft.Colors.WHITE,
            overlay_color=ft.Colors.with_opacity(0.08, Colors.ERROR),
            text_style=ft.TextStyle(font_family=FONT_FAMILY)
        )

class ContainerStyles:
    """Estilos de contenedores predefinidos."""
    
    @staticmethod
    def card(is_dark_theme=False):
        return {
            "bgcolor": Colors.DARK["surface"] if is_dark_theme else Colors.LIGHT["surface"],
            "border_radius": BORDER_RADIUS["container"],
            "padding": 20,
            "margin": ft.margin.only(top=8, bottom=8),
            "shadow": Shadows.MEDIUM
        }
    
    @staticmethod
    def dialog(is_dark_theme=False):
        return {
            "bgcolor": Colors.DARK["surface_dialog"] if is_dark_theme else Colors.LIGHT["surface_dialog"],
            "border_radius": BORDER_RADIUS["container"]
        }

class InputStyles:
    """Estilos de inputs predefinidos."""
    
    @staticmethod
    def dropdown(is_dark_theme=False):
        return {
            "filled": True,
            "color": Colors.DARK["on_surface"] if is_dark_theme else Colors.LIGHT["on_surface"],
            "bgcolor": Colors.DARK["surface"] if is_dark_theme else "#fbfbfb",
            "border_radius": BORDER_RADIUS["control"],
            "border_color": Colors.DARK["border"] if is_dark_theme else Colors.LIGHT["border"],
            "focused_border_color": Colors.PRIMARY,
            "content_padding": ft.padding.symmetric(vertical=8, horizontal=10),
            "text_style": ft.TextStyle(
                size=16,
                color=Colors.DARK["on_surface"] if is_dark_theme else Colors.LIGHT["on_surface"],
                font_family=FONT_FAMILY,
                weight=ft.FontWeight.W_500
            )
        }
    
    @staticmethod
    def textfield(is_dark_theme=False):
        return {
            "color": Colors.DARK["on_surface"] if is_dark_theme else Colors.LIGHT["on_surface"],
            "bgcolor": Colors.DARK["surface"] if is_dark_theme else "#fbfbfb",
            "border_radius": BORDER_RADIUS["control"],
            "border_color": Colors.DARK["border"] if is_dark_theme else Colors.LIGHT["border"],
            "focused_border_color": Colors.PRIMARY,
            "content_padding": ft.padding.symmetric(vertical=8, horizontal=10),
            "text_style": ft.TextStyle(
                color=Colors.DARK["on_surface"] if is_dark_theme else Colors.LIGHT["on_surface"],
                font_family=FONT_FAMILY
            )
        }

class ThemeManager:
    """Gestor de temas de la aplicación."""
    
    @staticmethod
    def get_theme_icon(is_dark_theme):
        return ft.Icons.WB_SUNNY if is_dark_theme else ft.Icons.NIGHTLIGHT_ROUND
    
    @staticmethod
    def get_theme_tooltip(is_dark_theme):
        return "Cambiar a tema claro" if is_dark_theme else "Cambiar a tema oscuro"
    
    @staticmethod
    def get_page_bgcolor(is_dark_theme):
        return Colors.DARK["background"] if is_dark_theme else Colors.LIGHT["background"]