# config.py
"""
Configuración y constantes de la aplicación de reportes meteorológicos.
"""

# Configuración de la aplicación
OPERADORES_FILE = "storage/operadores.json"
USER_CONFIG_FILE = "storage/user_config.json"
DEPARTAMENTO = "CEMUPRAD"

# Configuración de la ventana
WINDOW_CONFIG = {
    "width": 500,
    "height": 900,
    "resizable": False,
    "maximizable": False,
    "title": "Reporte del tiempo"
}

# Estados del tiempo
TIEMPO = [
    "Cielo despejado", 
    "Cielo parcialmente nublado", 
    "Cielo con nubosidad fragmentada",
    "Cielo con nubosidad dispersa", 
    "Cielo nublado",
    "Inicia evento meteorológico, precipitaciones de leve intensidad.",
    "Inicia evento meteorológico, precipitaciones de moderada intensidad",
    "Inicia evento meteorológico, precipitaciones de fuerte intensidad",
    "Se reporta el aumento de las precipitaciones de leves a moderadas",
    "Se reporta el aumento de las precipitaciones de moderadas a fuertes",
    "Se reporta disminución de las precipitaciones de moderadas a leves",
    "Se reporta disminución de las precipitaciones de fuertes a moderadas",
    "Finaliza evento meteorológico"
]

EMOJI_TIEMPO = [
    "☀", "⛅", "🌤", "🌤", "☁", "🌧", "🌧", "🌧", 
    "🌧", "🌧", "🌧", "🌧", "☁"
]

NOMBRES_TIEMPO = [
    "Despejado", "Parcialmente nublado", "Nubosidad fragmentada", 
    "Nubosidad dispersa", "Nublado", "Precipitaciones leves", 
    "Precipitaciones moderadas", "Precipitaciones fuertes",
    "Leves a moderadas", "Moderadas a fuertes", "Moderadas a leves", 
    "Fuertes a moderadas", "Cese de las precipitaciones"
]

# Cargos y jerarquías
def get_cargos(departamento: str) -> list[str]:
    """Genera la lista de cargos dinámicamente."""
    return [
        f"Analista de {departamento}",
        f"Auxiliar de {departamento}",
        f"Coordinador de {departamento}",
        "Jefe de los servicios",
        "Operador de radio"
    ]

JERARQUIAS = [
    "OPC", "OPC I", "OPC II", "OPC III",
    "OSPC I", "OSPC II", "OSPC III", 
    "OCPC I", "OCPC II"
]

# Municipios
MUNICIPIOS = [
    "Anaco", "Aragua", "Bolívar", "Bruzual", "Carvajal", "Cajigal",
    "Diego Bautista Urbaneja", "Freites", "Guanta", "Guanipa",
    "Independencia", "Libertad", "McGregor", "Miranda", "Monagas",
    "Peñalver", "Píritu", "San Juan de Capistrano", "Santa Ana",
    "Simón Rodríguez", "Sotillo"
]

# Configuración de estilos
FONT_FAMILY = "Segoe UI"
BORDER_RADIUS = {
    "container": 8,
    "control": 4
}