from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from forms import ProductoForm
from app.extensions import db, app, user_datastore
from app.models import Empleado, Usuario, Persona
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required
from flask_security.utils import login_user, logout_user
from utils.security import role_required

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/')
@login_required
@role_required('Administrador','Dueño', 'Cocinero','Cliente')
def index():
    productos = Productos.query.join(Categoria).filter(
        Categoria.estado == True,
        Productos.estado == True
    ).all()
    return render_template(('inventario/listProductos'))

@productos_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Dueño')
def registrar():
    form = ProductoForm