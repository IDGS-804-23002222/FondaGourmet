from . import productos
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from forms import CrearProductoForm, EditarProductoForm
from utils.security import role_required
from .services import (
    crear_producto, obtener_productos, desactivar_producto,
    activar_producto, obtener_producto, actualizar_producto, buscar_productos, obtener_categorias
)
from models import MateriaPrima


@productos.route('/', methods=['GET'])
@login_required
@role_required(1)
def index():
    """Listar todos los productos"""
    resultados, error = obtener_productos()
    if error:
        current_app.logger.error(f"Error al obtener productos: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('productos/index.html', productos=resultados, name=current_user.username)


@productos.route('/crear', methods=['GET', 'POST'])
@login_required
@role_required(1)
def crear():
    """Crear un nuevo producto"""
    form = CrearProductoForm()
    categorias, error = obtener_categorias()
    if error:
        current_app.logger.error(f"Error al obtener categorías: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('productos.index'))
    form.id_categoria_platillo.choices = [(cat.id_categoria_platillo, cat.nombre) for cat in categorias]
    materias_primas = MateriaPrima.query.filter_by(estado=True).order_by(MateriaPrima.nombre.asc()).all()
    
    if form.validate_on_submit():
        exito, error = crear_producto(form)
        
        if exito:
            current_app.logger.info(f"Producto creado: {form.nombre.data}")
            flash('Producto creado correctamente', 'success')
            return redirect(url_for('productos.index'))
        else:
            current_app.logger.error(f"Error al crear producto: {str(error)}")
            flash(error, 'danger')
    
    return render_template('productos/crear.html', form=form, materias_primas=materias_primas)


@productos.route('/editar', methods=['GET', 'POST'])
@login_required
@role_required(1)
def editar():
    """Editar un producto existente"""
    form = EditarProductoForm()
    
    id_producto = request.args.get('id_producto') or request.form.get('id_producto')
    if not id_producto:
        flash('No se recibió el producto a editar.', 'warning')
        return redirect(url_for('productos.index'))
    
    producto, error = obtener_producto(id_producto)
    if error:
        current_app.logger.error(f"Error al obtener producto para edición: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('productos.index'))
    
    if request.method == 'GET':
        form.nombre.data = producto.get('nombre')
        form.descripcion.data = producto.get('descripcion')
        form.precio.data = producto.get('precio')
        form.stock_actual.data = producto.get('stock_actual')
        form.stock_minimo.data = producto.get('stock_minimo')
        form.id_categoria_platillo.data = producto.get('id_categoria_platillo')
        form.imagen.data = producto.get('imagen')
    
    if request.method == 'POST' and form.validate_on_submit():
        exito, error = actualizar_producto(id_producto, form)
        
        if exito:
            current_app.logger.info(f"Producto actualizado: {form.nombre.data}")
            flash('Producto actualizado correctamente', 'success')
            return redirect(url_for('productos.index'))
        else:
            current_app.logger.error(f"Error al actualizar producto: {str(error)}")
            flash(error, 'danger')
    
    return render_template('productos/editar.html', form=form, producto=producto)


@productos.route('/desactivar', methods=['POST'])
@login_required
@role_required(1)
def desactivar():
    """Desactivar un producto"""
    id_producto = request.form.get('id_producto')
    
    exito, error = desactivar_producto(id_producto)
    
    if exito:
        current_app.logger.info(f"Producto desactivado: ID {id_producto}")
        flash('Producto desactivado', 'success')
    else:
        current_app.logger.error(f"Error al desactivar producto: {str(error)}")
        flash(error, 'danger')
    
    return redirect(url_for('productos.index'))


@productos.route('/activar', methods=['POST'])
@login_required
@role_required(1)
def activar():
    """Activar un producto"""
    id_producto = request.form.get('id_producto')
    
    exito, error = activar_producto(id_producto)
    
    if exito:
        current_app.logger.info(f"Producto activado: ID {id_producto}")
        flash('Producto activado', 'success')
    else:
        current_app.logger.error(f"Error al activar producto: {str(error)}")
        flash(error, 'danger')
    
    return redirect(url_for('productos.index'))


@productos.route('/detalles')
@login_required
@role_required(1)
def detalles():
    """Ver detalles de un producto"""
    id_producto = request.args.get('id_producto')
    producto, error = obtener_producto(id_producto)
    
    if error:
        current_app.logger.error(f"Error al obtener detalles del producto: {str(error)}")
        flash(error, 'danger')
        return redirect(url_for('productos.index'))
    
    return render_template('productos/detalles.html', producto=producto)
