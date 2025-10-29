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
    demanda = datos.get("demandas", [])

    lista_demandas = []

    if isinstance(demanda, str):
        lista_demandas.append({
            "texto": demanda.strip(),
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
    elif isinstance(demanda, list):
        for d in demanda:
            if isinstance(d, str):
                lista_demandas.append({
                    "texto": d.strip(),
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
            elif isinstance(d, dict) and "texto" in d:
                lista_demandas.append({
                    "texto": d["texto"].strip(),
                    "fecha": d.get("fecha", datetime.now().strftime("%d/%m/%Y %H:%M"))
                })

    # Combinar con demandas existentes y eliminar duplicados
    existentes = demandas.get(clave, [])
    todas = existentes + lista_demandas

    # Usar dict para eliminar duplicados por texto, conservar la última fecha
    deduplicadas = {}
    for d in todas:
        deduplicadas[d["texto"]] = d  # sobrescribe si ya existe

    # Guardar solo las demandas únicas
    demandas[clave] = list(deduplicadas.values())

# Guardar demandas actualizadas
with open(RUTA_DEMANDAS, "w", encoding="utf-8") as f:
    json.dump(demandas, f, ensure_ascii=False, indent=2)

print("✅ Todas las demandas convertidas, únicas y listas para el módulo de diagnóstico.")
