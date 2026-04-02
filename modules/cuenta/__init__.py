from flask import Blueprint

cuenta = Blueprint('cuenta', __name__)

from . import routes