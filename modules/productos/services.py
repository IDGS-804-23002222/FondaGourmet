from models import db, Producto, Categoria
from flask import current_app
import logging
import os

from utils.file_uploads import save_image_file

logger = logging.getLogger(__name__)

def crear_producto(form):
    """Crear un nuevo producto"""
    try:
        logger.info(f"Creando producto: {form.nombre.data}")
        
        # Verificar si el nombre ya existe
        producto_existente = Producto.query.filter_by(nombre=form.nombre.data).first()
        if producto_existente:
            return False, "Ya existe un producto con ese nombre."
        
        imagen_relativa = None
        imagen_file = form.imagen.data
        if imagen_file and getattr(imagen_file, 'filename', None):
            upload_root = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
            imagen_relativa, image_error = save_image_file(
                imagen_file,
                upload_root,
                'productos',
                current_app.config['ALLOWED_IMAGE_EXTENSIONS']
            )
            if image_error:
                return False, image_error

        nuevo_producto = Producto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data if form.descripcion.data else None,
            precio=form.precio.data,
            stock_actual=form.stock_actual.data,
            stock_minimo=form.stock_minimo.data,
            id_categoria=form.id_categoria.data,
            imagen=imagen_relativa,
            estado=True
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        logger.info(f"Producto creado exitosamente: {form.nombre.data}")
        return True, "Producto creado exitosamente"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear producto: {str(e)}")
        return False, str(e)


def obtener_productos(filtro_estado=None):
    """Obtener todos los productos"""
    try:
        query = Producto.query
        
        if filtro_estado is not None:
            query = query.filter_by(estado=filtro_estado)
        
        productos = query.all()
        
        resultado = []
        for prod in productos:
            resultado.append({
                'id_producto': prod.id_producto,
                'nombre': prod.nombre,
                'descripcion': prod.descripcion,
                'precio': prod.precio,
                'stock_actual': prod.stock_actual,
                'stock_minimo': prod.stock_minimo,
                'categoria_nombre': prod.categoria.nombre if prod.categoria else 'N/A',
                'id_categoria': prod.id_categoria,
                'imagen': prod.imagen,
                'estado': prod.estado,
                'fecha_creacion': prod.fecha_creacion,
                'estado_display': 'Activo' if prod.estado else 'Inactivo'
            })
        
        return resultado, None
        
    except Exception as e:
        logger.error(f"Error al obtener productos: {str(e)}")
        return None, str(e)


def obtener_producto(id_producto):
    """Obtener detalles de un producto específico"""
    try:
        producto = Producto.query.get(id_producto)
        
        if not producto:
            return None, "Producto no encontrado."
        
        resultado = {
            'id_producto': producto.id_producto,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': producto.precio,
            'stock_actual': producto.stock_actual,
            'stock_minimo': producto.stock_minimo,
            'categoria_nombre': producto.categoria.nombre if producto.categoria else 'N/A',
            'id_categoria': producto.id_categoria,
            'imagen': producto.imagen,
            'estado': producto.estado,
            'fecha_creacion': producto.fecha_creacion,
            'estado_display': 'Activo' if producto.estado else 'Inactivo'
        }
        
        return resultado, None
        
    except Exception as e:
        logger.error(f"Error al obtener producto: {str(e)}")
        return None, str(e)


def actualizar_producto(id_producto, form):
    """Actualizar un producto existente"""
    try:
        producto = Producto.query.get(id_producto)
        
        if not producto:
            return False, "Producto no encontrado."
        
        # Verificar si el nuevo nombre ya existe en otro producto
        if form.nombre.data and form.nombre.data != producto.nombre:
            producto_existente = Producto.query.filter_by(nombre=form.nombre.data).first()
            if producto_existente:
                return False, "Ya existe otro producto con ese nombre."
        
        logger.info(f"Actualizando producto: {id_producto}")
        
        if form.nombre.data:
            producto.nombre = form.nombre.data
        if form.descripcion.data:
            producto.descripcion = form.descripcion.data
        if form.precio.data:
            producto.precio = form.precio.data
        if form.stock_actual.data is not None:
            producto.stock_actual = form.stock_actual.data
        if form.stock_minimo.data is not None:
            producto.stock_minimo = form.stock_minimo.data
        if form.id_categoria.data:
            producto.id_categoria = form.id_categoria.data
        imagen_file = form.imagen.data
        if imagen_file and getattr(imagen_file, 'filename', None):
            upload_root = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
            imagen_relativa, image_error = save_image_file(
                imagen_file,
                upload_root,
                'productos',
                current_app.config['ALLOWED_IMAGE_EXTENSIONS']
            )
            if image_error:
                return False, image_error
            producto.imagen = imagen_relativa
        
        db.session.commit()
        logger.info(f"Producto actualizado: {id_producto}")
        return True, "Producto actualizado exitosamente"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar producto: {str(e)}")
        return False, str(e)


def desactivar_producto(id_producto):
    """Desactivar un producto (eliminación lógica)"""
    try:
        producto = Producto.query.get(id_producto)
        
        if not producto:
            return False, "Producto no encontrado."
        
        logger.info(f"Desactivando producto: {id_producto}")
        
        producto.estado = False
        db.session.commit()
        logger.info(f"Producto desactivado: {id_producto}")
        return True, "Producto desactivado exitosamente"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al desactivar producto: {str(e)}")
        return False, str(e)


def activar_producto(id_producto):
    """Activar un producto (recuperación lógica)"""
    try:
        producto = Producto.query.get(id_producto)
        
        if not producto:
            return False, "Producto no encontrado."
        
        logger.info(f"Activando producto: {id_producto}")
        
        producto.estado = True
        db.session.commit()
        logger.info(f"Producto activado: {id_producto}")
        return True, "Producto activado exitosamente"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al activar producto: {str(e)}")
        return False, str(e)


def buscar_productos(termino):
    """Buscar productos por nombre o descripción"""
    try:
        productos = Producto.query.filter(
            (Producto.nombre.ilike(f'%{termino}%')) |
            (Producto.descripcion.ilike(f'%{termino}%'))
        ).filter_by(estado=True).all()
        
        resultado = []
        for prod in productos:
            resultado.append({
                'id_producto': prod.id_producto,
                'nombre': prod.nombre,
                'descripcion': prod.descripcion,
                'precio': prod.precio,
                'stock_actual': prod.stock_actual,
                'stock_minimo': prod.stock_minimo,
                'categoria_nombre': prod.categoria.nombre if prod.categoria else 'N/A',
                'id_categoria': prod.id_categoria,
                'imagen': prod.imagen,
                'estado': prod.estado,
                'fecha_creacion': prod.fecha_creacion,
                'estado_display': 'Activo'
            })
        
        return resultado, None
        
    except Exception as e:
        logger.error(f"Error al buscar productos: {str(e)}")
        return None, str(e)
