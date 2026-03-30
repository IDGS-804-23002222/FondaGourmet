from flask import render_template
from . import reportes

@reportes.route('/')
def listar():
    return render_template('reportes/reportes.html')

@reportes.route('/detallado/<tipo>')
def detallado(tipo):
    return render_template('reportes/reporte_detallado.html', tipo=tipo)