from flask import render_template
from . import produccion

@produccion.route('/')
def listar():
    return render_template('produccion/produccion.html')

@produccion.route('/nueva')
def nueva():
    return render_template('produccion/nueva_orden.html')

@produccion.route('/ver/<int:id>')
def ver(id):
    return render_template('produccion/ver_orden.html', id=id)

@produccion.route('/iniciar/<int:id>')
def iniciar(id):
    return render_template('produccion/iniciar_orden.html', id=id)

@produccion.route('/completar/<int:id>')
def completar(id):
    return render_template('produccion/completar_orden.html', id=id)

@produccion.route('/cancelar/<int:id>')
def cancelar(id):
    return render_template('produccion/cancelar_orden.html', id=id)