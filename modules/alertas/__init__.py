from flask import Blueprint
from flask_login import current_user

from .services import construir_contexto_alertas

alertas = Blueprint('alertas', __name__)


def init_alertas(app):
    @app.context_processor
    def inject_alertas():
        return construir_contexto_alertas(current_user)


from . import routes