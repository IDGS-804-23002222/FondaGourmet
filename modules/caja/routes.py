from . import caja
from flask import render_template, flash
from flask_login import login_required, current_user
from utils.security import role_required
from models import Caja as CajaModel, MovimientoCaja, Venta


@caja.route('/', methods=['GET'])
@login_required
@role_required(1, 3)
def index():
    cajas = CajaModel.query.order_by(CajaModel.fecha.desc()).limit(10).all()
    return render_template('caja/caja.html', cajas=cajas)


@caja.route('/cierre', methods=['GET'])
@login_required
@role_required(1, 3)
def cierre():
    caja_abierta = CajaModel.query.filter_by(estado='Abierta').order_by(CajaModel.fecha.desc()).first()
    return render_template('caja/cierre_caja.html', caja=caja_abierta)


@caja.route('/historial', methods=['GET'])
@login_required
@role_required(1, 3)
def historial():
    cierres = CajaModel.query.filter_by(estado='Cerrada').order_by(CajaModel.fecha.desc()).all()
    return render_template('caja/historial_cierre.html', cierres=cierres)


@caja.route('/ver-cierre/<int:id_caja>', methods=['GET'])
@login_required
@role_required(1, 3)
def ver_cierre(id_caja):
    caja_registro = CajaModel.query.get_or_404(id_caja)
    return render_template('caja/ver_cierre.html', caja=caja_registro, id=id_caja)


@caja.route('/anular/<int:id_venta>', methods=['GET'])
@login_required
@role_required(1, 3)
def anular_venta(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    return render_template('caja/anular_venta.html', venta=venta, id=id_venta)
