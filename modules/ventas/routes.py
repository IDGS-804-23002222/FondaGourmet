from . import ventas
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario
from datetime import datetime

# ====================== LOGIN ======================
@ventas.route('/', methods=['GET', 'POST'])
def index():
    return render_template('ventas/index.html')
