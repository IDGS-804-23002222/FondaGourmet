from flask import Blueprint

mermas = Blueprint('mermas', __name__)

from . import routes
