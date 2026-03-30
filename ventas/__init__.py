from flask import Blueprint

ventas = Blueprint('ventas', __name__)

from . import routes