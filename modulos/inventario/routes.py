from flask import render_template
from . import inventario

@inventario.route('/')
def listar():
    return render_template('inventario/inventario.html')

@inventario.route('/nuevo-movimiento')
def nuevo_movimiento():
    return render_template('inventario/nuevo_movimiento.html')

@inventario.route('/movimientos/<int:id>')
def ver_movimientos(id):
    return render_template('inventario/ver_movimientos.html', id=id)

@inventario.route('/ajustar/<int:id>')
def ajustar(id):
    return render_template('inventario/ajustar_inventario.html', id=id)

@inventario.route('/informe')
def informe():
    return render_template('inventario/informe_inventario.html')