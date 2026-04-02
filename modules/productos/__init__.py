from flask import Blueprint

productos = Blueprint('productos', __name__)

from . import routes
