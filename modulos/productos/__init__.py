from flask import Blueprint

productos = Blueprint('productos', __name__, url_prefix='/productos')

from . import routes