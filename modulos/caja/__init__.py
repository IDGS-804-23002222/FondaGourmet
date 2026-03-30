from flask import Blueprint

caja = Blueprint('caja', __name__, url_prefix='/caja')

from . import routes