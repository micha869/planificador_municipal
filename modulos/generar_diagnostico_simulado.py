import json
import os
import random

# Lista de campos simulados
def datos_simulados():
    return {
        "demandas": random.choice(["Falta de agua", "Alumbrado", "Inseguridad", "Empleo", "Datos pendientes"]),
        "desarrollo_urbano": random.choice(["Crecimiento ordenado", "Desordenado", "No planificado"]),
        "servicios_basicos": random.choice(["Buenos", "Regulares", "Insuficientes"]),
        "medio_ambiente": random.choice(["Contaminación", "Reforestación activa", "Sin acciones"]),
        "economia": random.choice(["Agricultura", "Comercio", "Turismo", "Minería"]),
        "cohesion_social": random.choice(["Alta", "Media", "Baja", "Fragmentada"]),
        "condiciones_locales": random.choice(["Montañosa", "Costera", "Urbana", "Rural"]),
        "delimitacion_territorial": random.choice(["Conflictos limítrofes", "Bien definida"]),
        "caracteristicas_fisicas": random.choice(["Zona serrana", "Llanura", "Selva"]),
        "caracteristicas_sociales": random.choice(["Diversidad cultural", "Migración alta"]),
        "sostenibilidad_ambiental": random.choice(["Con proyectos", "Sin proyectos"]),
        "seguimiento_politicas": random.choice(["Evaluación parcial", "Buena implementación", "Sin seguimiento"]),
    }

# Cargar archivo original
ruta = os.path.join("data", "poblacion_guerrero.json")

with open(ruta, "r", encoding="utf-8") as f:
    datos = json.load(f)

# Actualizar cada municipio
for clave, municipio in datos.items():
    nuevos = datos_simulados()
    for campo, valor in nuevos.items():
        if municipio.get(campo, "Datos pendientes") == "Datos pendientes":
            municipio[campo] = valor

# Guardar archivo actualizado
with open(ruta, "w", encoding="utf-8") as f:
    json.dump(datos, f, indent=2, ensure_ascii=False)

print("Diagnóstico simulado completado para los municipios.")
