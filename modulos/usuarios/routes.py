from flask import render_template
from . import usuarios

@usuarios.route('/')
def listar():
    return render_template('usuarios/usuarios.html')

@usuarios.route('/nuevo')
def nuevo():
    return render_template('usuarios/nuevo_usuario.html')

@usuarios.route('/editar/<int:id>')
def editar(id):
    return render_template('usuarios/editar_usuario.html', id=id)

@usuarios.route('/eliminar/<int:id>')
def eliminar(id):
    return render_template('usuarios/eliminar_usuario.html', id=id)