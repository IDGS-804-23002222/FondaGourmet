from flask import render_template
from . import menu

@menu.route('/')
def listar():
    return render_template('menu/menu.html')

@menu.route('/agregar')
def agregar():
    return render_template('menu/agregar_menu.html')

@menu.route('/editar/<int:id>')
def editar(id):
    return render_template('menu/editar_menu.html', id=id)

@menu.route('/cambiar-disponibilidad/<int:id>')
def cambiar_disponibilidad(id):
    return render_template('menu/cambiar_disponibilidad.html', id=id)

@menu.route('/eliminar/<int:id>')
def eliminar(id):
    return render_template('menu/eliminar_menu.html', id=id)

@menu.route('/visualizar')
def visualizar():
    return render_template('menu/visualizar_menu.html')