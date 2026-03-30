from flask import Blueprint

inventario = Blueprint('inventario', __name__, url_prefix='/inventario')

from . import routes