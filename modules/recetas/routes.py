from . import recetas
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required
from utils.security import role_required
from .services import (
    obtener_recetas,
    obtener_receta_detalle,
    obtener_materias_activas,
    actualizar_receta_completa,
)


@recetas.route('/', methods=['GET'])
@login_required
@role_required(1, 2)
def index():
    recetas_list, error = obtener_recetas()
    if error:
        flash(error, 'danger')
        recetas_list = []
    return render_template('recetas/index.html', recetas=recetas_list)


@recetas.route('/ver/<int:id_receta>', methods=['GET'])
@login_required
@role_required(1, 2)
def ver(id_receta):
    receta, error = obtener_receta_detalle(id_receta)
    if error:
        flash(error, 'danger')
        return redirect(url_for('recetas.index'))
    return render_template('recetas/detalle.html', receta=receta)


@recetas.route('/editar/<int:id_receta>', methods=['GET', 'POST'])
@login_required
@role_required(1, 2)
def editar(id_receta):
    receta, error = obtener_receta_detalle(id_receta)
    if error:
        flash(error, 'danger')
        return redirect(url_for('recetas.index'))

    materias, error_materias = obtener_materias_activas()
    if error_materias:
        flash(error_materias, 'danger')
        return redirect(url_for('recetas.index'))

    if request.method == 'POST':
        rendimiento_raw = request.form.get('rendimiento')
        porciones_raw = request.form.get('porciones')
        nota = request.form.get('nota')
        estado = request.form.get('estado') == 'on'
        ids_materia = request.form.getlist('id_materia[]')
        cantidades = request.form.getlist('cantidad[]')

        detalles = []
        for idx, id_materia in enumerate(ids_materia):
            id_materia = (id_materia or '').strip()
            cantidad_raw = (cantidades[idx] if idx < len(cantidades) else '').strip()

            if not id_materia and not cantidad_raw:
                continue

            try:
                detalles.append({
                    'id_materia': int(id_materia),
                    'cantidad': float(cantidad_raw),
                })
            except (TypeError, ValueError):
                flash(f'Fila {idx + 1}: ingrediente o cantidad inválida.', 'warning')
                return render_template('recetas/editar.html', receta=receta, materias=materias)

        try:
            rendimiento = float(rendimiento_raw)
        except (TypeError, ValueError):
            flash('El rendimiento debe ser numérico.', 'warning')
            return render_template('recetas/editar.html', receta=receta, materias=materias)

        try:
            porciones = int(porciones_raw)
            if porciones <= 0:
                raise ValueError
        except (TypeError, ValueError):
            flash('El numero de porciones debe ser un entero mayor a cero.', 'warning')
            return render_template('recetas/editar.html', receta=receta, materias=materias)

        ok, mensaje = actualizar_receta_completa(
            id_receta=id_receta,
            rendimiento=rendimiento,
            porciones=porciones,
            nota=nota,
            detalles_payload=detalles,
            estado=estado,
        )

        if ok:
            flash(mensaje, 'success')
            return redirect(url_for('recetas.ver', id_receta=id_receta))

        flash(mensaje, 'danger')
        receta, _ = obtener_receta_detalle(id_receta)

    return render_template('recetas/editar.html', receta=receta, materias=materias)
