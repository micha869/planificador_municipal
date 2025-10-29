from flask import Blueprint, render_template, request

bp_escenarios = Blueprint('escenarios', __name__)

def parse_float(valor, default=0):
    try:
        return float(valor)
    except (ValueError, TypeError):
        return default

@bp_escenarios.route('/escenarios', methods=['GET'])
def escenarios():
    return render_template("escenarios.html")

@bp_escenarios.route('/escenarios/resultados', methods=['POST'])
def escenarios_resultados():
    # Datos del escenario
    nombre_foda = request.form.get('nombre_foda', '')
    nombre = request.form.get('nombre', '')
    estrategia = request.form.get('estrategia', '')
    impacto_directo = parse_float(request.form.get('impacto_directo'))
    impacto_indirecto = parse_float(request.form.get('impacto_indirecto'))

    # Datos FODA
    fortalezas = [f for f in request.form.getlist('fortalezas[]') if f.strip()]
    debilidades = [d for d in request.form.getlist('debilidades[]') if d.strip()]
    oportunidades = [o for o in request.form.getlist('oportunidades[]') if o.strip()]
    amenazas = [a for a in request.form.getlist('amenazas[]') if a.strip()]

    # Datos de problemas
    problemas = request.form.getlist('problemas[]')
    impacto_problemas = request.form.getlist('impacto_problemas[]')
    urgencia_problemas = request.form.getlist('urgencia_problemas[]')

    problemas_combinados = []
    for p, i, u in zip(problemas, impacto_problemas, urgencia_problemas):
        if p.strip():
            problemas_combinados.append({
                "problema": p.strip(),
                "impacto": parse_float(i),
                "urgencia": parse_float(u)
            })

    # Ordenar problemas por prioridad
    problemas_combinados.sort(key=lambda x: x['impacto'] + x['urgencia'], reverse=True)

    resultados = {
        "nombre_foda": nombre_foda,
        "nombre": nombre,
        "estrategia": estrategia,
        "impacto_directo": impacto_directo,
        "impacto_indirecto": impacto_indirecto,
        "foda": {
            "fortalezas": fortalezas,
            "debilidades": debilidades,
            "oportunidades": oportunidades,
            "amenazas": amenazas
        },
        "problemas_combinados": problemas_combinados,
        "interpretacion": "Simulación calculada con los datos ingresados."
    }

    return render_template("escenario_resultados.html", resultados=resultados)
