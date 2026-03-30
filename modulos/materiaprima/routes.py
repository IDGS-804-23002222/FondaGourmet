from flask import render_template
from . import materiaprima

@materiaprima.route('/')
def listar():
    return render_template('materiaprima/materiaprima.html')

@materiaprima.route('/nuevo')
def nuevo():
    return render_template('materiaprima/nuevo_ingrediente.html')

@materiaprima.route('/editar/<int:id>')
def editar(id):
    return render_template('materiaprima/editar_ingrediente.html', id=id)

@materiaprima.route('/ajustar-stock/<int:id>')
def ajustar_stock(id):
    return render_template('materiaprima/ajustar_stock.html', id=id)

@materiaprima.route('/eliminar/<int:id>')
def eliminar(id):
    return render_template('materiaprima/eliminar_ingrediente.html', id=id)

@materiaprima.route('/ver/<int:id>')
def ver(id):
    return render_template('materiaprima/ver_ingrediente.html', id=id)