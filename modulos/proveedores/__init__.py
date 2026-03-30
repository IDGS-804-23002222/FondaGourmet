from flask import Blueprint

proveedores = Blueprint('proveedores', __name__, url_prefix='/proveedores')

from . import routes