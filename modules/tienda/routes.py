from . import tienda
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario
from datetime import datetime

# ====================== LOGIN ======================
@tienda.route('/', methods=['GET', 'POST'])
def index():
    return render_template('tienda/index.html')

@tienda.route('/menu')
def menu():
    return render_template('tienda/menu.html')

@tienda.route('/pedidos')
def pedidos():
    return render_template('tienda/pedidos.html')