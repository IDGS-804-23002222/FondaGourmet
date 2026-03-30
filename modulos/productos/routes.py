from flask import render_template
from . import productos

@productos.route('/')
def listar():
    return render_template('productos/productos.html')

@productos.route('/nuevo')
def nuevo():
    return render_template('productos/nuevo_producto.html')

@productos.route('/editar/<int:id>')
def editar(id):
    return render_template('productos/editar_producto.html', id=id)

@productos.route('/eliminar/<int:id>')
def eliminar(id):
    return render_template('productos/eliminar_producto.html', id=id)

@productos.route('/ver/<int:id>')
def ver(id):
    return render_template('productos/ver_producto.html', id=id)