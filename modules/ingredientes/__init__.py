from flask import Blueprint

ingredientes = Blueprint('ingredientes', __name__)

from . import routes