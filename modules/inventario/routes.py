from flask import render_template
from flask_login import login_required, current_user

from utils.security import role_required
from . import inventario


@inventario.route('/', methods=['GET'])
@login_required
@role_required(1, 2, 3)
def index():
    puede_ver_materia_prima = current_user.id_rol in [1, 2]
    puede_ver_productos = current_user.id_rol in [1, 2, 3]

    return render_template(
        'inventario/index.html',
        puede_ver_materia_prima=puede_ver_materia_prima,
        puede_ver_productos=puede_ver_productos,
    )
