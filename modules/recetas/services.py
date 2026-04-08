from models import db, Receta, RecetaDetalle, MateriaPrima, Producto
import logging
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def obtener_recetas():
    try:
        recetas = Receta.query.order_by(Receta.fecha_creacion.desc()).all()
        resultado = []
        for receta in recetas:
            resultado.append({
                'id_receta': receta.id_receta,
                'producto_nombre': receta.producto.nombre if receta.producto else 'N/A',
                'rendimiento': receta.rendimiento,
                'estado': receta.estado,
                'fecha_creacion': receta.fecha_creacion,
                'detalles': [
                    {
                        'materia_nombre': detalle.materia_prima.nombre if detalle.materia_prima else 'N/A',
                        'cantidad': detalle.cantidad
                    }
                    for detalle in receta.detalles
                ]
            })
        return resultado, None
    except Exception as e:
        logger.error(f'Error al obtener recetas: {str(e)}')
        return None, str(e)


def crear_receta(id_producto, rendimiento=100, nota=None, detalles=None):
    """Crea una receta para un producto"""
    try:
        producto = Producto.query.get(id_producto)
        if not producto:
            return None, "Producto no encontrado"
        
        receta = Receta(
            id_producto=id_producto,
            rendimiento=rendimiento,
            nota=nota,
            estado=True
        )
        
        db.session.add(receta)
        db.session.flush()
        
        if detalles:
            for detalle in detalles:
                agregar_ingrediente_a_receta(
                    receta.id_receta,
                    detalle['id_materia'],
                    detalle['cantidad']
                )
        
        db.session.commit()
        return receta, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear receta: {str(e)}")
        return None, str(e)


def actualizar_receta(id_receta, rendimiento=None, nota=None):
    """Actualiza una receta existente"""
    try:
        receta = Receta.query.get(id_receta)
        if not receta:
            return None, "Receta no encontrada"
        
        if rendimiento is not None:
            receta.rendimiento = rendimiento
        if nota is not None:
            receta.nota = nota
        
        db.session.commit()
        return receta, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar receta: {str(e)}")
        return None, str(e)


def agregar_ingrediente_a_receta(id_receta, id_materia, cantidad):
    """Agrega un ingrediente a una receta"""
    try:
        receta = Receta.query.get(id_receta)
        materia = MateriaPrima.query.get(id_materia)
        
        if not receta or not materia:
            return None, "Receta o material no encontrado"
        
        existente = RecetaDetalle.query.filter_by(
            id_receta=id_receta,
            id_materia=id_materia
        ).first()
        
        if existente:
            existente.cantidad = cantidad
        else:
            detalle = RecetaDetalle(
                id_receta=id_receta,
                id_materia=id_materia,
                cantidad=cantidad
            )
            db.session.add(detalle)
        
        db.session.commit()
        return detalle, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al agregar ingrediente: {str(e)}")
        return None, str(e)


def calcular_costo_receta(id_receta):
    """Calcula el costo total de una receta"""
    try:
        receta = Receta.query.get(id_receta)
        if not receta:
            return 0
        
        costo_total = sum(
            detalle.cantidad * detalle.materia_prima.precio
            for detalle in receta.detalles
        )
        return costo_total
    except Exception as e:
        logger.error(f"Error al calcular costo: {str(e)}")
        return 0


def calcular_rendimiento_automatico(id_receta):
    """Calcula el rendimiento automáticamente"""
    try:
        receta = Receta.query.get(id_receta)
        if not receta or not receta.detalles:
            return 0
        
        cantidad_ingredientes = len(receta.detalles)
        return 50.0 if cantidad_ingredientes == 1 else (100.0 if cantidad_ingredientes > 0 else 0)
    except Exception as e:
        logger.error(f"Error al calcular rendimiento: {str(e)}")
        return 0


def serializar_receta(receta):
    """Serializa una receta para JSON"""
    if not receta:
        return None
    
    return {
        'id_receta': receta.id_receta,
        'id_producto': receta.id_producto,
        'producto_nombre': receta.producto.nombre if receta.producto else None,
        'rendimiento': receta.rendimiento,
        'nota': receta.nota,
        'estado': receta.estado,
        'fecha_creacion': receta.fecha_creacion.isoformat(),
        'detalles': [
            {
                'id_detalle': d.id_detalle,
                'ingrediente': d.materia_prima.nombre,
                'cantidad': d.cantidad,
                'unidad': d.materia_prima.unidad_medida,
                'precio': d.materia_prima.precio,
                'subtotal': d.cantidad * d.materia_prima.precio
            }
            for d in receta.detalles
        ],
        'costo_total': calcular_costo_receta(receta.id_receta)
    }
