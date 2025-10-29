import json
from datetime import datetime

# Archivos
RUTA_MUNICIPIOS = "data/municipios_guerrero.json"
RUTA_DEMANDAS = "data/demandas_ciudadanas.json"

# Cargar municipios
with open(RUTA_MUNICIPIOS, "r", encoding="utf-8") as f:
    municipios = json.load(f)

# Cargar demandas existentes (si ya hay)
try:
    with open(RUTA_DEMANDAS, "r", encoding="utf-8") as f:
        demandas = json.load(f)
except FileNotFoundError:
    demandas = {}

# Recorrer cada municipio y convertir sus demandas
for clave, datos in municipios.items():
    nombre = datos.get("municipio")
    demanda = datos.get("demandas", [])

    lista_demandas = []

    if isinstance(demanda, str):
        # Convertir string a dict
        lista_demandas.append({
            "texto": demanda,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
    elif isinstance(demanda, list):
        for d in demanda:
            if isinstance(d, str):
                lista_demandas.append({
                    "texto": d,
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
            elif isinstance(d, dict) and "texto" in d:
                # Mantener demanda ya con fecha
                lista_demandas.append(d)

    # Guardar en el JSON de demandas usando la CLAVE del municipio
    if lista_demandas:
        demandas[clave] = lista_demandas

# Guardar demandas actualizadas
with open(RUTA_DEMANDAS, "w", encoding="utf-8") as f:
    json.dump(demandas, f, ensure_ascii=False, indent=2)

print("✅ Todas las demandas están convertidas y listas para el módulo de diagnóstico.")
