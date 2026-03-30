from flask import Blueprint

produccion = Blueprint('produccion', __name__, url_prefix='/produccion')

from . import routes