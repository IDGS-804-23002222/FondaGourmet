from flask import Blueprint

materiaprima = Blueprint('materiaprima', __name__, url_prefix='/materiaprima')

from . import routes

 