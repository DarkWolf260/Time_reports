# config.py
"""
Configuración y constantes de la aplicación de reportes meteorológicos.
"""

# Configuración de la aplicación
DEPARTAMENTO = "Sala Situacional"

# Operadores por defecto
DEFAULT_OPERATORS = [
    {
        "nombre": "Rubén Rojas",
        "cargo": "Analista de Sala Situacional",
        "jerarquia": "OPC I",
        "cedula": "V-28.702.206"
    }
]

# Configuración de la ventana
WINDOW_CONFIG = {
    "width": 1700,
    "height": 800,
    "min_width": 850,
    "min_height": 800,
    "resizable": True,
    "maximizable": True,
    "title": "Reporte Meteorológico Estadal"
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
    "Finaliza evento meteorológico",
    "No se obtuvo información"
]

EMOJI_TIEMPO = [
    "☀", "⛅", "🌤", "🌤", "☁", "🌧", "🌧", "🌧",
    "🌧", "🌧", "🌧", "🌧", "☁",
    "❓"
]

NOMBRES_TIEMPO = [
    "Despejado", "Parcialmente nublado", "Nubosidad fragmentada",
    "Nubosidad dispersa", "Nublado", "Precipitaciones leves",
    "Precipitaciones moderadas", "Precipitaciones fuertes",
    "Leves a moderadas", "Moderadas a fuertes", "Moderadas a leves",
    "Fuertes a moderadas", "Cese de las precipitaciones",
    "Sin Información"
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

# Municipios por Eje
EJES = {
    "NORTE": [
        "Simón Bolívar",
        "Urbaneja",
        "Sotillo",
        "Guanta"
    ],
    "CENTRO": [
        "Anaco",
        "Libertad",
        "Aragua",
        "Mc Gregor",
        "Santa Ana",
        "Freites"
    ],
    "OESTE": [
        "Peñalver",
        "Piritu",
        "Cajigal",
        "Bruzual",
        "Carvajal",
        "Capistrano"
    ],
    "SUR": [
        "Guanipa",
        "Simón Rodríguez",
        "Miranda",
        "Independencia"
    ]
}

# Configuración de estilos
FONT_FAMILY = "Segoe UI"
BORDER_RADIUS = {
    "container": 8,
    "control": 4
}