from flask import Blueprint

usuarios = Blueprint('usuarios', __name__, url_prefix='/usuarios')

from . import routes

