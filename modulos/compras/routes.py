from flask import render_template
from . import compras

@compras.route('/')
def listar():
    return render_template('compras/compras.html')

@compras.route('/nueva')
def nueva():
    return render_template('compras/nueva_compra.html')

@compras.route('/ver/<int:id>')
def ver(id):
    return render_template('compras/ver_compra.html', id=id)

@compras.route('/editar/<int:id>')
def editar(id):
    return render_template('compras/editar_compra.html', id=id)

@compras.route('/recibir/<int:id>')
def recibir(id):
    return render_template('compras/recibir_compra.html', id=id)

@compras.route('/eliminar/<int:id>')
def eliminar(id):
    return render_template('compras/eliminar_compra.html', id=id)