from flask import Blueprint

reportes = Blueprint('reportes', __name__, url_prefix='/reportes')

from . import routes