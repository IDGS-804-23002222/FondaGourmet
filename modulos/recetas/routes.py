from flask import render_template
from . import recetas

@recetas.route('/')
def listar():
    return render_template('recetas/recetas.html')

@recetas.route('/nueva')
def nueva():
    return render_template('recetas/nueva_receta.html')

@recetas.route('/ver/<int:id>')
def ver(id):
    return render_template('recetas/ver_receta.html', id=id)

@recetas.route('/editar/<int:id>')
def editar(id):
    return render_template('recetas/editar_receta.html', id=id)

@recetas.route('/eliminar/<int:id>')
def eliminar(id):
    return render_template('recetas/eliminar_receta.html', id=id)