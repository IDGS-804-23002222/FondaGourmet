from flask import Blueprint

categorias = Blueprint('categorias', __name__, url_prefix='/categorias')

from . import routes