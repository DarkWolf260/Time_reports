import flet as ft
import json
import os
import datetime
import re
from estilos import *
from datos import *

# --- FUNCIÓN PARA CONVERTIR MARKDOWN A TEXTSPAN ---

def markdown_a_textspan(texto):
    patron = r'(\*.*?\*)|([^\*]+)'
    spans = []
    
    for match in re.finditer(patron, texto):
        if match.group(1):  # Texto entre asteriscos (negrita)
            texto_negrita = match.group(1).strip('*')
            spans.append(
                ft.TextSpan(
                    texto_negrita,
                    ft.TextStyle(
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO_CLARO
                    )
                )
            )
        elif match.group(2):  # Texto normal
            spans.append(ft.TextSpan(match.group(2)))
    
    return spans

# --- FUNCIONES PARA CARGAR Y GUARDAR OPERADORES ---

def cargar_operadores():
    if os.path.exists(OPERADORES_FILE):
        with open(OPERADORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_operadores(ops):
    with open(OPERADORES_FILE, "w", encoding="utf-8") as f:
        json.dump(ops, f, ensure_ascii=False, indent=4)

# --- CREACION DE LA VENTANA ---

def main(page: ft.Page):
    # Configuración de la ventana
    page.title = "Reporte del tiempo"
    page.window.width = 600
    page.window.height = 900
    page.window.resizable = False
    page.window.maximizable = False
    page.bgcolor = COLOR_FONDO_CLARO

    operadores = cargar_operadores()
    indice_tiempo = 0
    indice_operador = 0
    descripcion = TIEMPO[0]

    # Variable para almacenar el texto original con asteriscos
    texto_reporte_original = ""

    def obtener_nombres_operadores():
        return [op['nombre'] for op in operadores]

    def formatear_operador(op):
        return f"{op['cargo']} {op['jerarquia']} {op['nombre']} {op['cedula']}"

    # --- FUNCIONES DE LOS WIDGETS ---

    def actualizar_reporte():
        nonlocal texto_reporte_original
        fecha_actual = datetime.date.today().strftime('%d/%m/%Y')
        hora_actual = datetime.datetime.now().strftime('%H:%M')
        if operadores and 0 <= indice_operador < len(operadores):
            operador = formatear_operador(operadores[indice_operador])
        else:
            operador = "(Sin operador)"
        try:
            idx = int(campo_tiempo.value)
        except (TypeError, ValueError):
            idx = 0

        # Generar el texto original con asteriscos
        texto_reporte_original = f"*PROTECCIÓN CIVIL MUNICIPIO GUANTA* 🚨\n\n" \
                  f"*·   REPORTE DEL ESTADO DEL TIEMPO:* {EMOJI[idx]}\n" \
                  f"*·   FECHA:* {fecha_actual}\n" \
                  f"*·   HORA:* {hora_actual} HLV\n\n" \
                  f"*·   DESCRIPCIÓN:* {TIEMPO[idx]}\n\n" \
                  f"*·   NOVEDAD:* Sin novedades para la hora.\n\n" \
                  f"*·   REPORTA:* {operador}\n\n" \
                  f"*SOLO QUEREMOS SALVAR VIDAS 🚨🚑*"
        
        # Actualizar el widget Text con formato de negritas
        reporte_area.spans = markdown_a_textspan(texto_reporte_original)
        page.update()

    def copiar_reporte(e):
        # Copiar el texto original con asteriscos
        page.set_clipboard(texto_reporte_original)
        page.open(ft.SnackBar(ft.Text("¡Reporte copiado!", color=ft.Colors.GREEN)))
        page.update()

    # --- WIDGETS ---

    #  Área de texto para el reporte
    reporte_area = ft.Text(
        spans=[],
        size=17,
        color=COLOR_TEXTO_CLARO,
        font_family="Segoe UI",
        selectable=False
    )

    #  Control de selección de tiempo
    campo_tiempo = ft.Dropdown(
        width=380,
        options=[
            ft.dropdown.Option(
                key=str(i),
                text=f"{EMOJI[i]}  {n}"
            ) for i, n in enumerate(NOMBRES_TIEMPO)
        ],
        value="0",
        filled=True,
        color=COLOR_TEXTO_CLARO,
        bgcolor="#fbfbfb",
        border_radius=RADIO_CONTROL,
        border_color=COLOR_BORDE_CLARO,
        focused_border_color=COLOR_ACENTO,
        text_style=ft.TextStyle(size=16, color=COLOR_TEXTO_CLARO, font_family="Segoe UI", weight=ft.FontWeight.W_500)
    )
    
    #  Control de selección de operador
    campo_operador = ft.Dropdown(
        width=380,
        options=[ft.dropdown.Option(n) for n in obtener_nombres_operadores()],
        value=obtener_nombres_operadores()[indice_operador] if operadores else None,
        filled=True,
        color=COLOR_TEXTO_CLARO,
        bgcolor="#fbfbfb",
        border_radius=RADIO_CONTROL,
        border_color=COLOR_BORDE_CLARO,
        focused_border_color=COLOR_ACENTO,
        text_style=ft.TextStyle(size=16, color=COLOR_TEXTO_CLARO, font_family="Segoe UI")
    )

    # Botones
    boton_copiar = ft.FilledButton(
        "Copiar al Portapapeles",
        icon=ft.Icons.CONTENT_COPY,
        on_click=copiar_reporte,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=RADIO_CONTROL),
            bgcolor=COLOR_ACENTO,
            color=ft.Colors.WHITE,
            overlay_color=ft.Colors.with_opacity(0.08, COLOR_ACENTO),
            shadow_color=ft.Colors.with_opacity(0.15, COLOR_ACENTO),
            text_style=ft.TextStyle(font_family="Segoe UI"),
        )
    )

    boton_gestionar = ft.OutlinedButton(
        "Gestionar operadores",
        icon=ft.Icons.PEOPLE,
        on_click=lambda e: abrir_gestion_operadores(e),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=RADIO_CONTROL),
            bgcolor=COLOR_CONTENEDOR_CLARO,
            color=COLOR_ACENTO,
            overlay_color=ft.Colors.with_opacity(0.08, COLOR_ACENTO),
            shadow_color=ft.Colors.with_opacity(0.10, COLOR_ACENTO),
            side=ft.BorderSide(1, COLOR_ACENTO),
            text_style=ft.TextStyle(font_family="Segoe UI"),
        )
    )

    # Creditos
    creditos = ft.Text("Creado por: Rubén Rojas", size=13, italic=True, color=COLOR_TEXTO_CLARO, font_family="Segoe UI")

    def toggle_theme(e):
        # Verificar el tema actual
        if e.page.theme_mode == ft.ThemeMode.LIGHT:
            nuevo_tema = ft.ThemeMode.DARK
            nuevo_icono = ft.Icons.NIGHTLIGHT_ROUND
            icono_color = ft.Colors.GREY_300
        else:
            nuevo_tema = ft.ThemeMode.LIGHT
            nuevo_icono = ft.Icons.WB_SUNNY
            icono_color = ft.Colors.GREY_700
        
        # Actualizar el tema
        e.page.theme_mode = nuevo_tema

        # Actualizar el icono y su color
        e.control.icon = nuevo_icono
        e.control.icon_color = icono_color
    
        # Actualizar el texto del botón
        e.control.text = "Tema claro" if nuevo_tema == ft.ThemeMode.LIGHT else "Tema oscuro"
        
        # Guardar preferencia (opcional)
        e.page.client_storage.set("theme", "light" if nuevo_tema == ft.ThemeMode.LIGHT else "dark")
        
        # Actualizar la página
        e.page.update()

    # Recuperar tema guardado (opcional)
    saved_theme = page.client_storage.get("theme")
    if saved_theme == "dark":
        page.theme_mode = ft.ThemeMode.DARK
        icono_inicial = ft.Icons.NIGHTLIGHT_ROUND
        color_inicial = ft.Colors.GREY_300
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
        icono_inicial = ft.Icons.WB_SUNNY
        color_inicial = ft.Colors.GREY_700

    # Crear botón para cambiar tema
    Tema = ft.IconButton(
        icon=icono_inicial,
        icon_size=30,
        tooltip="Cambiar tema",
        on_click=toggle_theme,
        icon_color=color_inicial,
    )

    # --- AÑADIR WIDGETS A LA PÁGINA ---
    page.add(
        ft.Column([Tema,
            ft.Container(ft.Column([ft.Text("REPORTE DEL TIEMPO", size=32, weight=ft.FontWeight.W_700, color=COLOR_TEXTO_CLARO, font_family="Segoe UI"),
                reporte_area],
                alignment="center", horizontal_alignment="center", spacing=12),
                bgcolor=COLOR_CONTENEDOR_CLARO,
                border_radius=RADIO_CONTENEDOR,
                padding=20,
                margin=ft.margin.only(top=8, bottom=8),
                shadow=SOMBRA,
            ),
            ft.Container(
                ft.Column([
                    ft.Text("Datos del reporte", size=18, weight=ft.FontWeight.W_600, color=COLOR_TEXTO_CLARO, font_family="Segoe UI"),
                    campo_tiempo,
                    campo_operador,
                    boton_gestionar
                ], alignment="center", horizontal_alignment="center", spacing=12),
                bgcolor=COLOR_CONTENEDOR_CLARO,
                border_radius=RADIO_CONTENEDOR,
                padding=20,
                margin=ft.margin.only(top=8, bottom=8),
                shadow=SOMBRA,
                width=500,
                alignment=ft.alignment.center
            ),
            ft.Row([
                boton_copiar
            ], alignment="center", vertical_alignment="center"),
            ft.Row([
                creditos
            ], alignment="center", vertical_alignment="center")
        ], expand=True, alignment="center", horizontal_alignment="center", spacing=18)
    )
    # Forzar actualización inicial
    actualizar_reporte()

    def on_tiempo_change(e):
        nonlocal indice_tiempo, descripcion
        try:
            idx = int(campo_tiempo.value)
        except (TypeError, ValueError):
            idx = 0
        indice_tiempo = idx
        descripcion = TIEMPO[idx]
        actualizar_reporte()
    campo_tiempo.on_change = on_tiempo_change

    def on_operador_change(e):
        nonlocal indice_operador
        indice_operador = obtener_nombres_operadores().index(campo_operador.value)
        actualizar_reporte()
    campo_operador.on_change = on_operador_change

    def abrir_gestion_operadores(e):
        nombre_op = ft.TextField(label="Nombre", width=250, color=ft.Colors.BLACK, text_style=ft.TextStyle(color=ft.Colors.BLACK, font_family="Segoe UI"), hint_text="Nombre del operador", multiline=False)
        cedula_op = ft.TextField(label="Cédula", width=250, color=ft.Colors.BLACK, text_style=ft.TextStyle(color=ft.Colors.BLACK, font_family="Segoe UI"), hint_text="Cédula", multiline=False)
        campo_cargo = ft.Dropdown(label="Cargo", width=250, options=[ft.dropdown.Option(c) for c in CARGOS], value=CARGOS[0], text_style=ft.TextStyle(color=ft.Colors.BLACK))
        campo_jerarquia = ft.Dropdown(label="Jerarquía", width=250, options=[ft.dropdown.Option(j) for j in JERARQUIAS], value=JERARQUIAS[0], text_style=ft.TextStyle(color=ft.Colors.BLACK))
        campo_gestionar = ft.Dropdown(label="Eliminar operador", width=250, options=[ft.dropdown.Option(n) for n in obtener_nombres_operadores()], text_style=ft.TextStyle(color=ft.Colors.BLACK))

        def agregar_op(ev):
            nonlocal indice_operador
            nombre = nombre_op.value.strip()
            cedula = cedula_op.value.strip()
            cargo = campo_cargo.value
            jerarquia = campo_jerarquia.value
            if nombre and cedula and cargo and jerarquia:
                operadores.append({
                    "nombre": nombre,
                    "cargo": cargo,
                    "jerarquia": jerarquia,
                    "cedula": cedula
                })
                guardar_operadores(operadores)
                nuevos_nombres = obtener_nombres_operadores()
                campo_operador.options = [ft.dropdown.Option(n) for n in nuevos_nombres]
                campo_operador.value = nombre
                indice_operador = nuevos_nombres.index(nombre)
                campo_gestionar.options = [ft.dropdown.Option(n) for n in nuevos_nombres]
                campo_gestionar.value = None
                dlg.content.controls = [
                    nombre_op, cedula_op, campo_cargo, campo_jerarquia,
                    ft.Row([
                        ft.ElevatedButton("Añadir", on_click=agregar_op, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=RADIO_CONTROL), color=COLOR_TEXTO_CLARO, bgcolor=COLOR_ACENTO, overlay_color=ft.Colors.with_opacity(0.08, COLOR_ACENTO))),
                    ], alignment="center", vertical_alignment="center"),
                    ft.Divider(),
                    campo_gestionar,
                    ft.Row([
                        ft.ElevatedButton("Eliminar", on_click=eliminar_op, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=RADIO_CONTROL), bgcolor=ft.Colors.RED_400, color=COLOR_TEXTO_CLARO, overlay_color=ft.Colors.with_opacity(0.08, ft.Colors.RED_400))),
                    ], alignment="center", vertical_alignment="center"),
                ]
                page.snack_bar = ft.SnackBar(ft.Text("Operador añadido", color=ft.Colors.GREEN))
                page.snack_bar.open = True
                page.update()
                actualizar_reporte()

        def eliminar_op(ev):
            nonlocal indice_operador
            idx = None
            nombres = obtener_nombres_operadores()
            seleccionado = campo_gestionar.value
            if seleccionado in nombres:
                idx = nombres.index(seleccionado)
            if idx is not None and 0 <= idx < len(operadores):
                operador_actual = campo_operador.value
                operadores.pop(idx)
                guardar_operadores(operadores)
                nuevos_nombres = obtener_nombres_operadores()
                campo_operador.options = [ft.dropdown.Option(n) for n in nuevos_nombres]
                campo_gestionar.options = [ft.dropdown.Option(n) for n in nuevos_nombres]
                if not nuevos_nombres:
                    campo_operador.value = None
                    indice_operador = 0
                else:
                    if operador_actual == seleccionado:
                        campo_operador.value = nuevos_nombres[0]
                        indice_operador = 0
                    else:
                        if indice_operador >= len(nuevos_nombres):
                            indice_operador = len(nuevos_nombres) - 1
                campo_gestionar.value = None
                dlg.content.controls = [
                    nombre_op, cedula_op, campo_cargo, campo_jerarquia,
                    ft.Row([
                        ft.ElevatedButton("Añadir", on_click=agregar_op, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=RADIO_CONTROL), color=COLOR_TEXTO_CLARO, bgcolor=COLOR_ACENTO, overlay_color=ft.Colors.with_opacity(0.08, COLOR_ACENTO))),
                    ], alignment="center", vertical_alignment="center"),
                    ft.Divider(),
                    campo_gestionar,
                    ft.Row([
                        ft.ElevatedButton("Eliminar", on_click=eliminar_op, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=RADIO_CONTROL), bgcolor=ft.Colors.RED_400, color=COLOR_TEXTO_CLARO, overlay_color=ft.Colors.with_opacity(0.08, ft.Colors.RED_400))),
                    ], alignment="center", vertical_alignment="center"),
                ]
                page.snack_bar = ft.SnackBar(ft.Text("Operador eliminado", color=ft.Colors.ORANGE))
                page.snack_bar.open = True
                page.update()
                actualizar_reporte()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Gestión de Operadores", weight="bold", color=COLOR_TEXTO_CLARO, font_family="Segoe UI"),
            content=ft.Column([
                nombre_op, cedula_op, campo_cargo, campo_jerarquia,
                ft.Row([
                    ft.ElevatedButton(
                        "Añadir",
                        on_click=agregar_op,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=RADIO_CONTROL),
                            color=COLOR_TEXTO_CLARO,
                            bgcolor=COLOR_ACENTO,
                            overlay_color=ft.Colors.with_opacity(0.08, COLOR_ACENTO),
                            text_style=ft.TextStyle(font_family="Segoe UI")
                        )
                    )
                ], alignment="center", vertical_alignment="center"),
                ft.Divider(),
                campo_gestionar,
                ft.Row([
                    ft.ElevatedButton(
                        "Eliminar",
                        on_click=eliminar_op,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=RADIO_CONTROL),
                            bgcolor=ft.Colors.RED_400,
                            color=COLOR_TEXTO_CLARO,
                            overlay_color=ft.Colors.with_opacity(0.08, ft.Colors.RED_400),
                            text_style=ft.TextStyle(font_family="Segoe UI")
                        )
                    )
                ], alignment="center", vertical_alignment="center")
            ], tight=True, width=300, alignment="center", horizontal_alignment="center"),
            actions=[
                ft.ElevatedButton(
                    "Cerrar",
                    on_click=lambda e: page.close(dlg),
                    style=ft.ButtonStyle(
                        color=COLOR_TEXTO_CLARO,
                        shape=ft.RoundedRectangleBorder(radius=RADIO_CONTROL),
                        text_style=ft.TextStyle(font_family="Segoe UI")
                    )
                )
            ],
            actions_alignment="center",
            shape=ft.RoundedRectangleBorder(radius=RADIO_CONTENEDOR),
            bgcolor="#ffffff",
        )
        page.open(dlg)

if __name__ == "__main__":
    ft.app(target=main)