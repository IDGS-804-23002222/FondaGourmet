from flask import Blueprint

recetas = Blueprint('recetas', __name__, url_prefix='/recetas')

from . import routes