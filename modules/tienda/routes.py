from . import tienda
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from utils.security import role_required


@tienda.route('/', methods=['GET', 'POST'])
def index():
    return render_template('tienda/index.html')

@tienda.route('/menu')
def menu():
    return render_template('tienda/menu.html')
