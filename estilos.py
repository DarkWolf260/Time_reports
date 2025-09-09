import flet as ft



CLARO = "#ffffff"
OSCURO = "#1b1b1b"

# Paleta y estilos principales
COLOR_FONDO_CLARO = "#f3f3f3"
COLOR_FONDO_CLARO_DIALOGO = "#afafaf"
COLOR_CONTENEDOR_CLARO = "#f9f9f9"
COLOR_BORDE_CLARO = ft.Colors.BLUE_GREY_100
COLOR_ACENTO = "#005a9e"
COLOR_TEXTO_CLARO = ft.Colors.BLACK

COLOR_FONDO_OSCURO = ft.Colors.with_opacity(0.98, ft.Colors.BLUE_GREY_900)
COLOR_CONTENEDOR_OSCURO = ft.Colors.with_opacity(0.98, ft.Colors.BLUE_GREY_800)
COLOR_BORDE_OSCURO = ft.Colors.BLUE_GREY_700
COLOR_TEXTO_OSCURO = ft.Colors.WHITE
COLOR_ACENTO_OSCURO = ft.Colors.BLUE_300

RADIO_CONTENEDOR = 8
RADIO_CONTROL = 4
SOMBRA = ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.10, ft.Colors.BLUE_GREY_900), offset=ft.Offset(0, 4))

FUENTE = "Segoe UI"

# Estilos de texto
TEXTO_TITULO = ft.TextStyle(size=18, weight=ft.FontWeight.W_600, color=COLOR_TEXTO_CLARO, font_family=FUENTE)
TEXTO_NORMAL = lambda color=COLOR_TEXTO_CLARO: ft.TextStyle(size=16, color=color, font_family=FUENTE)
TEXTO_INPUT = lambda color=COLOR_TEXTO_CLARO: ft.TextStyle(size=17, color=color, font_family=FUENTE)


# Sombra

SOMBRA = ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK), offset=ft.Offset(0, 4))



Tema = ft.IconButton(
    icon=ft.Icons.SUNNY,
    tooltip="Cambiar tema",
    on_click=lambda e: cambiar_tema()
)

def cambiar_tema():
    if Tema.icon_color == CLARO:
        Tema.icon = ft.Icons.DARK_MODE
        Tema.icon_color = OSCURO
        Tema.tooltip = "Cambiar a tema claro"
        ft.Page.theme_mode = ft.ThemeMode.DARK
        page.update()
    else:
        Tema.icon = ft.Icons.SUNNY
        Tema.icon_color = CLARO
        Tema.tooltip = "Cambiar a tema oscuro"
        ft.Page.theme_mode = ft.ThemeMode.LIGHT
        page.update()
