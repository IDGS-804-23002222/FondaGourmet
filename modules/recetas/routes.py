from . import recetas
from flask import render_template, flash
from flask_login import login_required
from utils.security import role_required
from .services import obtener_recetas


@recetas.route('/', methods=['GET'])
@login_required
@role_required(1, 2)
def index():
    recetas_list, error = obtener_recetas()
    if error:
        flash(error, 'danger')
        recetas_list = []
    return render_template('recetas/index.html', recetas=recetas_list)
