import csv
import json
import random
from collections import defaultdict

ruta_csv = r"C:\Users\Francisca\Documents\plandedasorrollo\planificador_municipal\data\ITER_12CSV20.csv"

# Diccionario por municipio
municipios = defaultdict(lambda: {
    "poblacion_total": 0,
    "viviendas": 0,
    "poblacion_indigena": 0,
    "rezago_educativo_sum": 0.0,
    "rezago_educativo_count": 0,
    "salud_sum": 0,
    "salud_count": 0,
    "pobreza_sum": 0,
    "pobreza_count": 0
})

# Funciones para parsear valores
def parse_float(valor, default=None):
    try:
        return float(valor)
    except (ValueError, TypeError):
        return default

def parse_int(valor, default=None):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return default

with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        mun = row["NOM_MUN"].strip()
        poblacion = parse_int(row.get("POBTOT"), 0)
        viviendas = parse_int(row.get("VIVTOT"), 0)
        poblacion_indigena = parse_int(row.get("PHOG_IND"), 0)

        municipios[mun]["poblacion_total"] += poblacion
        municipios[mun]["viviendas"] += viviendas
        municipios[mun]["poblacion_indigena"] += poblacion_indigena

        rez = parse_float(row.get("PROM_HNV"))
        if rez is not None:
            municipios[mun]["rezago_educativo_sum"] += rez
            municipios[mun]["rezago_educativo_count"] += 1

        salud = parse_int(row.get("PDER_SS"))
        if salud is not None:
            municipios[mun]["salud_sum"] += salud
            municipios[mun]["salud_count"] += 1

        pob = parse_int(row.get("PCON_DISC"))
        if pob is not None:
            municipios[mun]["pobreza_sum"] += pob
            municipios[mun]["pobreza_count"] += 1

# Crear JSON final solo por municipio
datos_municipios = {}
for i, (mun, datos) in enumerate(municipios.items(), start=1):
    clave = f"12{str(i).zfill(3)}"
    rez_educ = (datos["rezago_educativo_sum"] / max(1, datos["rezago_educativo_count"]))
    salud = (datos["salud_sum"] / max(1, datos["salud_count"]))
    pobreza = (datos["pobreza_sum"] / max(1, datos["pobreza_count"]))

    datos_municipios[clave] = {
        "municipio": mun,
        "poblacion_total": datos["poblacion_total"],
        "viviendas": datos["viviendas"],
        "rezago_educativo": round(rez_educ,2),
        "pobreza": int(pobreza),
        "salud": int(salud),
        "seguridad": random.choices(["Alta","Media","Baja"], weights=[0.2,0.5,0.3])[0],
        "poblacion_indigena": datos["poblacion_indigena"],
        "marginacion": random.choices(["Baja","Media","Alta"], weights=[0.2,0.5,0.3])[0],
        "imparticion_justicia": random.choices(["Buena","Limitada"], weights=[0.3,0.7])[0],
        "indice_desarrollo": round(random.uniform(0.55,0.78),2),
        "demandas": "Participación en programas municipales",
        "desarrollo_urbano": "Datos aproximados de CONAPO y cartografía",
        "servicios_basicos": "Datos de agua, luz y drenaje",
        "medio_ambiente": "Áreas verdes y zonas protegidas",
        "economia": "Predominan servicios y comercio local",
        "cohesion_social": "Eventos comunitarios y participación ciudadana",
        "condiciones_locales": "Clima y geografía promedio",
        "delimitacion_territorial": "Según INEGI",
        "caracteristicas_fisicas": "Relieve, ríos y montañas",
        "caracteristicas_sociales": "Población mestiza e indígena",
        "participacion_ciudadana": random.choices(["Alta","Media","Baja"], weights=[0.3,0.5,0.2])[0],
        "sostenibilidad_ambiental": "Programas de reciclaje y reforestación",
        "seguimiento_politicas": "Reportes de gobierno municipal y CONEVAL"
    }

# Guardar JSON
with open("data/municipios_guerrero.json","w",encoding="utf-8") as f:
    json.dump(datos_municipios, f, ensure_ascii=False, indent=2)

print(f"✅ JSON generado con {len(datos_municipios)} municipios de Guerrero")