from . import dashboard
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from utils.security import role_required


@dashboard.route('/', methods=['GET', 'POST'])
@login_required
@role_required(1)
def index():
    return render_template('dashboard/index.html')

