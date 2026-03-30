from flask import render_template
from . import ventas

@ventas.route('/')
def listar():
    return render_template('ventas/ventas.html')

@ventas.route('/nueva')
def nueva():
    return render_template('ventas/nueva_venta.html')

@ventas.route('/ver/<int:id>')
def ver(id):
    return render_template('ventas/ver_venta.html', id=id)

@ventas.route('/editar/<int:id>')
def editar(id):
    return render_template('ventas/editar_venta.html', id=id)

@ventas.route('/eliminar/<int:id>')
def eliminar(id):
    return render_template('ventas/eliminar_venta.html', id=id)

@ventas.route('/imprimir/<int:id>')
def imprimir(id):
    return render_template('ventas/imprimir_ticket.html', id=id)