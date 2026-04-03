from . import produccion
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario
from datetime import datetime

# ====================== LOGIN ======================
@produccion.route('/', methods=['GET', 'POST'])
def index():
    return render_template('produccion/index.html')
