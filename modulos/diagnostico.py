# modulos/diagnostico.py
import json
import os

def obtener_diagnostico(clave_municipio):
    ruta = os.path.join('data', 'poblacion_guerrero.json')
    if not os.path.exists(ruta):
        return None

    with open(ruta, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)

    return datos.get(clave_municipio)
