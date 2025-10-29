import os, json
from datetime import datetime
from flask import flash, Blueprint, render_template, request, redirect, url_for

# ===== RUTAS DE ARCHIVOS =====
DATA_DIR = "data"
RUTA_MUNICIPIOS = os.path.join(DATA_DIR, "municipios_guerrero.json")
RUTA_CACHE = os.path.join(DATA_DIR, "diagnostico_cache.json")
RUTA_DEMANDAS = os.path.join(DATA_DIR, "demandas_ciudadanas.json")

# ===== INDICADORES =====
INDICADORES_CRITICOS = ["pobreza", "rezago_educativo", "salud"]
OTROS_INDICADORES = ["poblacion_total", "viviendas", "seguridad", "poblacion_indigena", "marginacion"]
CAMPOS_EXTRA = [
    'desarrollo_urbano', 'servicios_basicos', 'medio_ambiente',
    'economia', 'cohesion_social', 'condiciones_locales', 'delimitacion_territorial',
    'caracteristicas_fisicas', 'caracteristicas_sociales', 'participacion_ciudadana',
    'sostenibilidad_ambiental', 'seguimiento_politicas'
]

# ===== CREAR CARPETAS Y ARCHIVOS SI NO EXISTEN =====
os.makedirs(DATA_DIR, exist_ok=True)
for ruta in [RUTA_CACHE, RUTA_DEMANDAS]:
    if not os.path.exists(ruta):
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

# ===== FUNCIONES =====
def cargar_demandas(clave_municipio):
    """Carga demandas de un municipio por su clave"""
    with open(RUTA_DEMANDAS, 'r', encoding='utf-8') as f:
        todas = json.load(f)
    return todas.get(clave_municipio, [])

def guardar_demanda(clave_municipio, texto):
    """Agrega una demanda ciudadana usando la clave del municipio, evita duplicados"""
    texto = texto.strip()
    if not texto:
        return
    with open(RUTA_DEMANDAS, 'r', encoding='utf-8') as f:
        todas = json.load(f)
    if clave_municipio not in todas:
        todas[clave_municipio] = []

    # Eliminar duplicados por texto (mantener la fecha más reciente)
    todas[clave_municipio] = [d for d in todas[clave_municipio] if d["texto"] != texto]

    todas[clave_municipio].append({
        "texto": texto,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    with open(RUTA_DEMANDAS, 'w', encoding='utf-8') as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    flash("✅ Demanda agregada correctamente", "success")

def sincronizar_cache(clave_municipio=None):
    """Actualiza automáticamente la cache con los datos más recientes del JSON de municipios"""
    if not os.path.exists(RUTA_MUNICIPIOS):
        return
    
    # Cargar JSON de municipios
    with open(RUTA_MUNICIPIOS, 'r', encoding='utf-8') as f:
        municipios = json.load(f)
    
    # Cargar cache existente
    cache = {}
    if os.path.exists(RUTA_CACHE):
        with open(RUTA_CACHE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    
    # Actualizar cache municipio por municipio
    claves = [clave_municipio] if clave_municipio else municipios.keys()
    for clave in claves:
        if clave in municipios:
            datos = municipios[clave]
            if clave in cache:
                # Mantener demandas
                demandas = cache[clave].get('demandas', [])
                cache[clave].update(datos)
                cache[clave]['demandas'] = demandas
            else:
                cache[clave] = datos
                cache[clave]['demandas'] = []

    # Guardar cache actualizado
    with open(RUTA_CACHE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def obtener_diagnostico_completo(clave_municipio):
    """Genera diagnóstico completo por municipio"""
    resultado = {}

    # Sincronizar cache automáticamente antes de cargar el diagnóstico
    sincronizar_cache(clave_municipio)

    # Revisar cache
    cache = {}
    if os.path.exists(RUTA_CACHE):
        with open(RUTA_CACHE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            if clave_municipio in cache:
                resultado = cache[clave_municipio]

    # Cargar datos del JSON de municipios si no está en cache (caso extremo)
    if not resultado and os.path.exists(RUTA_MUNICIPIOS):
        with open(RUTA_MUNICIPIOS, 'r', encoding='utf-8') as f:
            municipios = json.load(f)
            if clave_municipio in municipios:
                resultado.update(municipios[clave_municipio])

    # Indicadores
    for ind in INDICADORES_CRITICOS + OTROS_INDICADORES:
        resultado[ind] = resultado.get(ind, "Sin datos")

    # Campos extra
    for campo in CAMPOS_EXTRA:
        resultado[campo] = resultado.get(campo, "N/A")

    # Cargar demandas usando clave
    resultado['demandas'] = cargar_demandas(clave_municipio)

    # Guardar nombre y clave
    resultado["municipio"] = resultado.get("municipio", "N/A")
    resultado["clave"] = clave_municipio

    # Guardar en cache
    cache[clave_municipio] = resultado
    with open(RUTA_CACHE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    return resultado

def obtener_todos_municipios():
    """Devuelve lista de todos los municipios con clave y nombre"""
    municipios = []
    if os.path.exists(RUTA_MUNICIPIOS):
        with open(RUTA_MUNICIPIOS, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            municipios = [{"clave": clave, "nombre": info.get("municipio", "Sin nombre")}
                          for clave, info in datos.items()]
    return municipios

# ===== DEFINICIÓN DEL BLUEPRINT =====
bp_diagnostico = Blueprint('diagnostico', __name__, template_folder='../templates')

# ===== RUTAS =====
@bp_diagnostico.route('/diagnostico', methods=['GET', 'POST'])
def ruta_diagnostico():
    resultado = None
    municipios = obtener_todos_municipios()

    clave = request.form.get('municipio') if request.method == 'POST' else request.args.get('municipio')
    if clave:
        resultado = obtener_diagnostico_completo(clave)

    return render_template('diagnostico.html', municipios=municipios, resultado=resultado)

@bp_diagnostico.route('/diagnostico/agregar_demanda', methods=['POST'])
def agregar_demanda_ruta():
    clave = request.form.get('municipio')
    texto = request.form.get('nueva_demanda')
    if clave and texto:
        guardar_demanda(clave, texto)
    # Redirigir pasando la clave como argumento GET para recargar el diagnóstico con demandas
    return redirect(url_for('diagnostico.ruta_diagnostico', municipio=clave))
