from flask import Blueprint

compras = Blueprint('compras', __name__, url_prefix='/compras')

from . import routes