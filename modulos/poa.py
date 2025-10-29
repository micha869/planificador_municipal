# modulos/poa.py
import os
import json
from flask import Blueprint, render_template, request, jsonify

bp_poa = Blueprint('poa', __name__, url_prefix='/poa')

DATA_FILE = os.path.join(os.path.dirname(__file__), 'poa_data.json')

def leer_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_datos(metas):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metas, f, ensure_ascii=False, indent=4)

@bp_poa.route('/', methods=['GET', 'POST'])
def poa_principal():
    mensaje = None
    metas = leer_datos()

    if request.method == 'POST':
        nueva_actividad = {
            'objetivo': request.form.get('objetivo'),
            'actividad': request.form.get('actividad'),
            'responsable': request.form.get('responsable'),
            'fecha_inicio': request.form.get('fecha_inicio'),
            'fecha_fin': request.form.get('fecha_fin'),
            'recursos': request.form.get('recursos'),
            'indicador': request.form.get('indicador')
        }
        metas.append(nueva_actividad)
        guardar_datos(metas)
        mensaje = "✅ Actividad agregada correctamente"

    return render_template('poa.html', mensaje=mensaje, metas=metas)

# Nueva ruta AJAX para guardar cambios en la tabla
@bp_poa.route('/actualizar', methods=['POST'])
def actualizar_poa():
    datos = request.json
    if datos:
        guardar_datos(datos)
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400
