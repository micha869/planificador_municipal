from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import json
import os
import sys


# Agregar carpeta 'modulos' al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))
from generador_plan import generar_plan_pdf
from diagnostico import obtener_diagnostico




app = Flask(__name__)
app.secret_key = "clave_super_secreta"
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

USUARIOS_FILE = "usuarios.json"
if not os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, 'w') as f:
        json.dump({}, f)

def archivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------- RUTAS -------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Sesión cerrada correctamente.")
    return redirect(url_for('index'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        with open(USUARIOS_FILE, 'r+') as file:
            try:
                usuarios = json.load(file)
            except json.JSONDecodeError:
                usuarios = {}
            if usuario in usuarios:
                flash('Usuario ya registrado')
            else:
                usuarios[usuario] = contrasena
                file.seek(0)
                json.dump(usuarios, file)
                file.truncate()
                flash('Registro exitoso')
                return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        with open(USUARIOS_FILE) as file:
            usuarios = json.load(file)
            if usuario in usuarios and usuarios[usuario] == contrasena:
                session['usuario'] = usuario
                return redirect(url_for('dashboard'))
            else:
                flash('Credenciales incorrectas')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    autorizado = False
    correo = session['usuario']
    try:
        with open('usuarios_autorizados.json', 'r') as f:
            usuarios_autorizados = json.load(f)
        autorizado = correo in usuarios_autorizados
    except:
        autorizado = False

    return render_template('dashboard.html', autorizado=autorizado)

@app.route('/diagnostico', methods=['GET', 'POST'])
def diagnostico():
    resultado = None
    municipios = []
    ruta = os.path.join('data', 'poblacion_guerrero.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            municipios = [{"clave": clave, "nombre": info["municipio"]} for clave, info in datos.items()]
    if request.method == 'POST':
        clave = request.form['municipio']
        resultado = obtener_diagnostico(clave)
    return render_template('diagnostico.html', municipios=municipios, resultado=resultado)

@app.route('/arbol')
def arbol():
    return render_template('arbol.html')

@app.route('/marco-logico')
def marco_logico():
    return render_template('marco_logico.html')

@app.route('/arbol_marco')
def arbol_marco():
    return render_template('arbol_marco.html')

@app.route('/cursos')
def cursos():
    return render_template('cursos.html')

@app.route('/curso_marco_logico')
def curso_marco_logico():
    return render_template('curso_marco_logico.html')

@app.route('/plan')
def plan_generado():
    archivo_pdf = "plan_municipal.pdf"
    archivo_word = "plan_municipal.docx"
    ruta_pdf = os.path.join('data', archivo_pdf)
    ruta_word = os.path.join('data', archivo_word)
    existe_pdf = os.path.exists(ruta_pdf)
    existe_word = os.path.exists(ruta_word)
    return render_template('plan_generado.html', archivo_pdf=archivo_pdf, archivo_word=archivo_word, existe_pdf=existe_pdf, existe_word=existe_word)

@app.route('/generar-plan')
def generar_plan():
    generar_plan_pdf()
    flash("✅ Plan generado correctamente.")
    return redirect(url_for('plan_generado'))

@app.route('/descargar-plan-pdf')
def descargar_plan_pdf():
    return _descargar_archivo('plan_municipal.pdf')

@app.route('/descargar-plan-word')
def descargar_plan_word():
    return _descargar_archivo('plan_municipal.docx')

@app.route('/vista-previa-plan')
def vista_previa_plan():
    return _descargar_archivo('plan_municipal.pdf', as_attachment=False)

@app.route('/descargar-plan')
def descargar_plan():
    return _descargar_archivo('plan_municipal.pdf')

@app.route('/guia-plan')
def guia_plan():
    return render_template('plan_guia.html')

@app.route('/subir_archivo', methods=['POST'])
def subir_archivo():
    if 'archivo' not in request.files:
        flash('No se seleccionó archivo')
        return redirect(url_for('curso_marco_logico'))
    archivo = request.files['archivo']
    if archivo.filename == '' or not archivo_permitido(archivo.filename):
        flash('Archivo inválido o tipo no permitido')
        return redirect(url_for('curso_marco_logico'))
    ruta = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
    archivo.save(ruta)
    flash('Archivo subido con éxito')
    return redirect(url_for('curso_marco_logico'))

@app.route('/taller_diagnostico')
def taller_diagnostico():
    return render_template('taller_diagnostico.html')

@app.route('/admin_taller_diagnostico', methods=['GET', 'POST'])
def admin_taller_diagnostico():
    ruta_json = 'data/modulos_diagnostico.json'

    if os.path.exists(ruta_json):
        with open(ruta_json, 'r', encoding='utf-8') as f:
            modulos = json.load(f)
    else:
        modulos = []

    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        video = request.files['video']
        pdf = request.files['pdf']

        if video:
            video_path = os.path.join('static/videos', video.filename)
            video.save(video_path)
        if pdf:
            pdf_path = os.path.join('static/pdfs', pdf.filename)
            pdf.save(pdf_path)

        nuevo_modulo = {
            "titulo": titulo,
            "descripcion": descripcion,
            "video": f"videos/{video.filename}",
            "pdf": f"pdfs/{pdf.filename}"
        }
        modulos.append(nuevo_modulo)

        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(modulos, f, ensure_ascii=False, indent=2)

        flash('✅ Módulo agregado correctamente')
        return redirect(url_for('admin_taller_diagnostico'))

    return render_template('taller_admin.html', modulos=modulos)

def _descargar_archivo(nombre, as_attachment=True):
    return send_from_directory('data', nombre, as_attachment=as_attachment)
@app.route('/curso_presupuesto_resultados', methods=['GET', 'POST'])
def curso_presupuesto_resultados():
    # Lista de módulos ejemplo (puedes cambiarlo)
    modulos_pbr = [
        {
            'titulo': '💰 Introducción al PbR',
            'descripcion': 'Conceptos básicos del Presupuesto basado en Resultados y su importancia.',
            'video': 'videos/introduccion_pbr.mp4',
            'pdf': 'pdfs/introduccion_pbr.pdf'
        },
    ]
    
    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo')
            return redirect(url_for('curso_presupuesto_resultados'))
        archivo = request.files['archivo']
        if archivo.filename == '' or not archivo_permitido(archivo.filename):
            flash('Archivo inválido o tipo no permitido')
            return redirect(url_for('curso_presupuesto_resultados'))
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
        archivo.save(ruta_guardado)
        flash('Archivo subido con éxito')
        return redirect(url_for('curso_presupuesto_resultados'))
    
    return render_template('curso_presupuesto_resultados.html', modulos_pbr=modulos_pbr)
@app.route('/evaluacion_desempeno')
def evaluacion_desempeno():
    return render_template('evaluacion_desempeno.html')

@app.route("/marco-juridico")
def marco_juridico():
    return render_template("marco_juridico.html")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

