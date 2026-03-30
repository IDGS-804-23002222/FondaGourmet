from flask import render_template
from . import proveedores

@proveedores.route('/')
def listar():
    return render_template('proveedores/proveedores.html')

@proveedores.route('/nuevo')
def nuevo():
    return render_template('proveedores/nuevo_proveedor.html')

@proveedores.route('/editar/<int:id>')
def editar(id):
    return render_template('proveedores/editar_proveedor.html', id=id)

@proveedores.route('/eliminar/<int:id>')
def eliminar(id):
    return render_template('proveedores/eliminar_proveedor.html', id=id)

@proveedores.route('/ver/<int:id>')
def ver(id):
    return render_template('proveedores/ver_proveedor.html', id=id)