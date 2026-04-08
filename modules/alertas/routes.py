from flask import jsonify, session
from flask_login import login_required, current_user

from . import alertas
from .services import marcar_alertas_vistas


@alertas.route('/marcar-vistas', methods=['GET'])
@login_required
def marcar_vistas():
    try:
        marcar_alertas_vistas(current_user, session)
        return jsonify({'ok': True})
    except Exception:
        return jsonify({'ok': False}), 500