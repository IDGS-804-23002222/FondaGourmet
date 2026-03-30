from flask import render_template
from . import caja

@caja.route('/')
def listar():
    return render_template('caja/caja.html')

@caja.route('/cierre')
def cierre():
    return render_template('caja/cierre_caja.html')

@caja.route('/anular/<int:id>')
def anular(id):
    return render_template('caja/anular_venta.html', id=id)

@caja.route('/historial')
def historial():
    return render_template('caja/historial_cierres.html')

@caja.route('/ver-cierre/<int:id>')
def ver_cierre(id):
    return render_template('caja/ver_cierre.html', id=id)