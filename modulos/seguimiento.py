from flask import Blueprint, render_template

bp_seguimiento = Blueprint('seguimiento_mod', __name__)

@bp_seguimiento.route('/seguimiento')
def seguimiento():
    return render_template('seguimiento.html')