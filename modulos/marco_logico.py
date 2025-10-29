from flask import Blueprint, render_template

bp_marco_logico = Blueprint('marco_logico_mod', __name__)

@bp_marco_logico.route('/marco-logico')
def marco_logico():
    return render_template('marco_logico.html')