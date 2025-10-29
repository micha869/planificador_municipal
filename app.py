# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os, json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import timedelta
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from werkzeug.security import generate_password_hash, check_password_hash
from modulos.diagnostico import obtener_diagnostico_completo

# ------------------- CONFIG -------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave_super_secreta")
app.permanent_session_lifetime = timedelta(days=30)

# ------------------- BASE DE DATOS -------------------
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql+psycopg://usuario:password@host:port/dbname"
engine = create_engine(DATABASE_URL, echo=True, future=True)

# Crear tabla usuarios si no existe
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            usuario VARCHAR(100) UNIQUE,
            contrasena VARCHAR(200),
            fecha_registro TIMESTAMP DEFAULT NOW()
        );
    """))

# ------------------- BLUEPRINTS OAuth -------------------
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/oauth2/google"
)
facebook_bp = make_facebook_blueprint(
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    scope=["email"],
    redirect_url="/oauth2/facebook"
)

app.register_blueprint(google_bp, url_prefix="/login")
app.register_blueprint(facebook_bp, url_prefix="/login")

# ------------------- RUTAS -------------------
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file, flash, redirect, url_for

def generar_plan_pdf():
    """Genera un PDF básico del Plan Municipal."""
    carpeta_data = "data"
    if not os.path.exists(carpeta_data):
        os.makedirs(carpeta_data)

    ruta_pdf = os.path.join(carpeta_data, "plan_municipal.pdf")

    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "PLAN DE DESARROLLO MUNICIPAL")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "Documento generado automáticamente por el Sistema de Planeación Estratégica Municipal.")
    c.drawString(100, 690, "Incluye módulos: Diagnóstico, Árbol de Problemas, Marco Lógico, Escenarios y POA.")
    c.save()

    return ruta_pdf


@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Sesión cerrada correctamente.")
    return redirect(url_for('index'))

# ---------- Registro tradicional ----------
@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")

        if not usuario or not contrasena:
            flash("Por favor, llena todos los campos.")
            return redirect(url_for("registrar"))

        contrasena_hash = generate_password_hash(contrasena)

        try:
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO usuarios (usuario, contrasena) VALUES (:u, :c)"),
                    {"u": usuario, "c": contrasena_hash},
                )
            flash("Usuario registrado exitosamente.")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Error al registrar: {e}")
            return redirect(url_for("registrar"))

    return render_template("registrar.html")

# ---------- Login tradicional ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")

        with engine.begin() as conn:
            result = conn.execute(
                text("SELECT * FROM usuarios WHERE usuario=:usuario"),
                {"usuario": usuario},
            ).mappings().first()

        if result and check_password_hash(result["contrasena"], contrasena):
            session.permanent = True
            session["usuario"] = usuario
            flash("Inicio de sesión exitoso.")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos.")
            return redirect(url_for("login"))

    return render_template("login.html")

# ---------- Login con Google ----------
@app.route("/login/google")
def login_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        info = resp.json()
        usuario = info.get("email")
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO usuarios (usuario, contrasena)
                VALUES (:usuario, '')
                ON CONFLICT (usuario) DO NOTHING
            """), {"usuario": usuario})
        session.permanent = True
        session['usuario'] = usuario
        return redirect(url_for("dashboard"))
    flash("No se pudo iniciar sesión con Google")
    return redirect(url_for("login"))

# ---------- Login con Facebook ----------
@app.route("/login/facebook")
def login_facebook():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("/me?fields=id,name,email")
    if resp.ok:
        info = resp.json()
        usuario = info.get("email", info.get("id"))
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO usuarios (usuario, contrasena)
                VALUES (:usuario, '')
                ON CONFLICT (usuario) DO NOTHING
            """), {"usuario": usuario})
        session.permanent = True
        session['usuario'] = usuario
        return redirect(url_for("dashboard"))
    flash("No se pudo iniciar sesión con Facebook")
    return redirect(url_for("login"))

# ---------- Dashboard ----------
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    correo = session['usuario']
    autorizado = False

    try:
        with open('usuarios_autorizados.json', 'r') as f:
            usuarios_autorizados = json.load(f)
        autorizado = correo in usuarios_autorizados
    except FileNotFoundError:
        autorizado = False

    return render_template('dashboard.html', autorizado=autorizado)


from flask import Flask, render_template, request, redirect, url_for, flash
from modulos.diagnostico import (
    obtener_diagnostico_completo,
    obtener_todos_municipios,
    guardar_demanda,
    sincronizar_cache  # ✅ Importar la función de sincronización
)

@app.route('/diagnostico', methods=['GET', 'POST'])
def ruta_diagnostico():
    resultado = None
    municipios = obtener_todos_municipios()

    # Revisar si viene clave por GET (después de agregar demanda)
    clave = request.args.get('municipio')

    if request.method == 'POST':
        clave = request.form.get('municipio')

    if clave:
        # 🔹 Actualizar cache automáticamente antes de obtener diagnóstico
        sincronizar_cache(clave)
        resultado = obtener_diagnostico_completo(clave)

    return render_template('diagnostico.html', municipios=municipios, resultado=resultado)

@app.route('/diagnostico/agregar_demanda', methods=['POST'])
def agregar_demanda_ruta():
    municipio = request.form.get('municipio')
    texto = request.form.get('nueva_demanda')
    if municipio and texto:
        guardar_demanda(municipio, texto)
        flash("✅ Demanda agregada correctamente", "success")
    # Redirige al diagnóstico pasando la clave para que cargue el resultado
    return redirect(url_for('ruta_diagnostico', municipio=municipio))

# ---------- Funciones auxiliares y resto de rutas ----------
def _descargar_archivo(nombre, as_attachment=True):
    return send_from_directory('data', nombre, as_attachment=as_attachment)

# Puedes agregar aquí tus rutas de arbol, marco-logico, cursos, etc., igual que en tu código original

@app.route('/arbol')
def arbol():
    return render_template('arbol.html')

@app.route('/arbol_marco')
def arbol_marco():
    return render_template('arbol_marco.html')

@app.route('/cursos')
def cursos():
    return render_template('cursos.html')

@app.route('/curso_marco_logico')
def curso_marco_logico():
    modulos = [
        {
            "titulo": "📘 Introducción al Marco Lógico",
            "descripcion": "Breve presentación del concepto y utilidad del Marco Lógico.",
            "pdf": "pdfs/introduccion_marco_logico.pdf"
        },
        {
            "titulo": "📗 Teoría del Marco Lógico",
            "descripcion": "Elementos teóricos detrás del Marco Lógico.",
            "pdf": "pdfs/teoria_marco_logico.pdf"
        },
        {
            "titulo": "📙 Cómo hacer un proyecto",
            "descripcion": "Aplicación práctica para formular un proyecto paso a paso.",
            "pdf": "pdfs/como_hacer_un_proyecto.pdf"
        }
    ]
    return render_template('curso_marco_logico.html', modulos=modulos)

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
        video = request.files.get('video', None)
        pdf = request.files.get('pdf', None)

        if video and archivo_permitido(video.filename):
            video_path = os.path.join('static/videos', video.filename)
            video.save(video_path)
        else:
            flash('Video inválido o no seleccionado')
            return redirect(url_for('admin_taller_diagnostico'))

        if pdf and archivo_permitido(pdf.filename):
            pdf_path = os.path.join('static/pdfs', pdf.filename)
            pdf.save(pdf_path)
        else:
            flash('PDF inválido o no seleccionado')
            return redirect(url_for('admin_taller_diagnostico'))

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
# ------------------- RUTAS Y BLUEPRINTS DE MÓDULOS -------------------

# ------------------- BLUEPRINTS NUEVOS -------------------
from modulos.arbolp import bp_arbolp
from modulos.marco_logico import bp_marco_logico
from modulos.poa import bp_poa
from modulos.seguimiento import bp_seguimiento
from modulos.escenarios import bp_escenarios
from modulos.diagnostico import bp_diagnostico
# Registrar cada blueprint
app.register_blueprint(bp_diagnostico)
app.register_blueprint(bp_arbolp)
app.register_blueprint(bp_marco_logico)
app.register_blueprint(bp_poa)
app.register_blueprint(bp_seguimiento)
app.register_blueprint(bp_escenarios)
# ------------------- MAIN -------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)