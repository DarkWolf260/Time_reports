import flet as ft

def main(page: ft.Page):
    # Configurar página
    page.title = "Windows 11 Style App"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Tema claro de Windows 11
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#0078D4",
            on_primary="#FFFFFF",
            surface="#FFFFFF",
            on_surface="#202020",
            surface_tint="#0078D4",
            surface_container_high="#F3F2F1",  # Reemplaza surface_variant
            on_surface_variant="#616161",
            outline="#D2D0CE",
        ),
        text_theme=ft.TextTheme(
            body_medium=ft.TextStyle(
                color="#202020",
                size=14
            ),
            title_medium=ft.TextStyle(
                color="#202020",
                size=16,
                weight="bold"
            ),
            label_medium=ft.TextStyle(
                color="#616161",
                size=12
            )
        )
    )
    
    # Tema oscuro de Windows 11
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#0086F0",
            on_primary="#FFFFFF",
            surface="#202020",
            on_surface="#FFFFFF",
            surface_tint="#0086F0",
            surface_container_high="#2B2B2B",  # Reemplaza surface_variant
            on_surface_variant="#C8C6C4",
            outline="#454545",
        ),
        text_theme=ft.TextTheme(
            body_medium=ft.TextStyle(
                color="#FFFFFF",
                size=14
            ),
            title_medium=ft.TextStyle(
                color="#FFFFFF",
                size=16,
                weight="bold"
            ),
            label_medium=ft.TextStyle(
                color="#C8C6C4",
                size=12
            )
        )
    )
    
    # Función para cambiar tema
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        theme_button.icon = ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
        theme_button.text = "Modo oscuro" if page.theme_mode == ft.ThemeMode.LIGHT else "Modo claro"
        page.update()
    
    # Botón para cambiar tema
    theme_button = ft.FilledButton(
        icon=ft.Icons.DARK_MODE,
        text="Modo oscuro",
        on_click=toggle_theme,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )
    )
    
    # Crear controles con estilo Windows 11
    title = ft.Text("Windows 11 Style Controls", 
                   size=24, 
                   weight="bold")
    
    subtitle = ft.Text("Estos controles imitan el estilo de Windows 11",
                      size=14,
                      color=ft.Colors.ON_SURFACE_VARIANT)
    
    # Campo de texto con estilo Windows 11
    text_field = ft.TextField(
        label="Campo de texto",
        value="Texto de ejemplo",
        border_radius=6,
        border_color=ft.Colors.OUTLINE,
        focused_border_color=ft.Colors.PRIMARY,
        content_padding=ft.padding.all(12),
        text_style=ft.TextStyle(size=14),
        label_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
        width=300
    )
    
    # Botones con estilo Windows 11
    primary_button = ft.FilledButton(
        "Botón primario",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )
    )
    
    secondary_button = ft.OutlinedButton(
        "Botón secundario",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )
    )
    
    switch = ft.Switch(
        label="Interruptor",
        value=True,
        thumb_color={ft.ControlState.SELECTED: ft.Colors.PRIMARY},
        # Corregido: with_opacity es un método de instancia, no de clase
        track_color={ft.ControlState.SELECTED: "#0078D480"},  # 50% opacity
        height=30
    )
    
    # Checkbox con estilo Windows 11 - CORREGIDO
    checkbox = ft.Checkbox(
        label="Casilla de verificación",
        value=True,
        check_color=ft.Colors.ON_PRIMARY,
        fill_color={ft.ControlState.SELECTED: ft.Colors.PRIMARY},
    )
    
    
    # Radio buttons con estilo Windows 11
    radio_group = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="opcion1", label="Opción 1"),
            ft.Radio(value="opcion2", label="Opción 2"),
            ft.Radio(value="opcion3", label="Opción 3"),
        ]),
    )
    
    # Slider con estilo Windows 11
    slider = ft.Slider(
        min=0,
        max=100,
        value=50,
        active_color=ft.Colors.PRIMARY,
        inactive_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        thumb_color=ft.Colors.PRIMARY,
    )
    
    # Dropdown con estilo Windows 11
    dropdown = ft.Dropdown(
        label="Lista desplegable",
        options=[
            ft.dropdown.Option("Opción 1"),
            ft.dropdown.Option("Opción 2"),
            ft.dropdown.Option("Opción 3"),
        ],
        border_radius=6,
        border_color=ft.Colors.OUTLINE,
        focused_border_color=ft.Colors.PRIMARY,
        text_style=ft.TextStyle(size=14),
        label_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
        width=200
    )
    
    # Tarjeta con estilo Windows 11
    card = ft.Container(
        content=ft.Column([
            ft.Text("Tarjeta de ejemplo", weight="bold", size=16),
            ft.Text("Esta es una tarjeta con el estilo de Windows 11", size=14),
            ft.Row([primary_button, secondary_button], spacing=10)
        ], spacing=12),
        padding=20,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )
    
    # Agrupar controles
    controls_column = ft.Column([
        title,
        subtitle,
        ft.Divider(height=20),
        text_field,
        ft.Row([primary_button, secondary_button], spacing=10),
        ft.Row([switch, checkbox], spacing=20),
        ft.Text("Grupo de opciones:", style="labelMedium"),
        radio_group,
        ft.Text("Control deslizante:", style="labelMedium"),
        slider,
        dropdown,
        ft.Divider(height=20),
        card
    ], spacing=16)
    
    # Añadir a la página
    page.add(
        ft.Row([theme_button], alignment="end"),
        controls_column
    )
    
    # Forzar actualización inicial
    page.update()

ft.app(target=main)