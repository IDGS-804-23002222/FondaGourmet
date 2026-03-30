from flask import render_template
from . import categorias

@categorias.route('/')
def listar():
    return render_template('categorias/categorias.html')

@categorias.route('/nueva')
def nueva():
    return render_template('categorias/nueva_categoria.html')

@categorias.route('/ver/<int:id>')
def ver(id):
    return render_template('categorias/ver_categoria.html', id=id)

@categorias.route('/editar/<int:id>')
def editar(id):
    return render_template('categorias/editar_categoria.html', id=id)

@categorias.route('/eliminar/<int:id>')
def eliminar(id):
    return render_template('categorias/eliminar_categoria.html', id=id)