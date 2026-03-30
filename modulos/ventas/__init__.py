from flask import Blueprint

ventas = Blueprint('ventas', __name__, url_prefix='/ventas')

from . import routes