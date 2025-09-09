# --- DATOS Y CONSTANTES ---

departamento = "CEMUPRAD"

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

EMOJI = ["☀", "⛅", "🌤", "🌤", "☁", "🌧", "🌧", "🌧", "🌧", "🌧", "🌧", "🌧", "☁"]

NOMBRES_TIEMPO = [
    "Despejado", "Parcialmente nublado", "Nubosidad fragmentada", "Nubosidad dispersa",
    "Nublado", "Precipitaciones leves", "Precipitaciones moderadas", "Precipitaciones fuertes",
    "Leves a moderadas", "Moderadas a fuertes", "Moderadas a leves", "Fuertes a moderadas",
    "Cese de las precipitaciones"
]

CARGOS = [
    f"Analista {departamento}",
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


OPERADORES_FILE = "operadores.json"
