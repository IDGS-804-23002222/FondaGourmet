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
                'porciones': int(receta.porciones or 1),
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


def crear_receta(id_producto, rendimiento=100, porciones=1, nota=None, detalles=None):
    """Crea una receta para un producto"""
    try:
        producto = Producto.query.get(id_producto)
        if not producto:
            return None, "Producto no encontrado"
        
        receta = Receta(
            id_producto=id_producto,
            rendimiento=rendimiento,
            porciones=porciones,
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


def actualizar_receta(id_receta, rendimiento=None, porciones=None, nota=None):
    """Actualiza una receta existente"""
    try:
        receta = Receta.query.get(id_receta)
        if not receta:
            return None, "Receta no encontrada"
        
        if rendimiento is not None:
            receta.rendimiento = rendimiento
        if porciones is not None:
            receta.porciones = porciones
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
        'porciones': int(receta.porciones or 1),
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


def obtener_receta_detalle(id_receta):
    try:
        receta = Receta.query.get(id_receta)
        if not receta:
            return None, "Receta no encontrada"

        data = {
            'id_receta': receta.id_receta,
            'id_producto': receta.id_producto,
            'producto_nombre': receta.producto.nombre if receta.producto else 'N/A',
            'rendimiento': float(receta.rendimiento or 0),
            'porciones': int(receta.porciones or 1),
            'nota': receta.nota,
            'estado': bool(receta.estado),
            'fecha_creacion': receta.fecha_creacion,
            'detalles': [
                {
                    'id_detalle': detalle.id_detalle,
                    'id_materia': detalle.id_materia,
                    'materia_nombre': detalle.materia_prima.nombre if detalle.materia_prima else 'N/A',
                    'unidad': detalle.materia_prima.unidad_medida if detalle.materia_prima else '',
                    'precio': float(detalle.materia_prima.precio or 0) if detalle.materia_prima else 0,
                    'cantidad': float(detalle.cantidad or 0),
                    'subtotal': float(detalle.cantidad or 0) * float(detalle.materia_prima.precio or 0) if detalle.materia_prima else 0,
                }
                for detalle in receta.detalles
            ],
        }
        data['costo_total'] = sum(item['subtotal'] for item in data['detalles'])
        return data, None
    except Exception as e:
        logger.error(f"Error al obtener detalle de receta: {str(e)}")
        return None, str(e)


def obtener_materias_activas():
    try:
        materias = (
            MateriaPrima.query
            .filter_by(estado=True)
            .order_by(MateriaPrima.nombre.asc())
            .all()
        )
        return materias, None
    except Exception as e:
        logger.error(f"Error al obtener materias activas: {str(e)}")
        return None, str(e)


def actualizar_receta_completa(id_receta, rendimiento, porciones, nota, detalles_payload, estado=True):
    try:
        receta = Receta.query.get(id_receta)
        if not receta:
            return False, "Receta no encontrada"

        if rendimiento is None or float(rendimiento) < 0:
            return False, "El rendimiento debe ser un valor válido"

        if porciones is None or int(porciones) <= 0:
            return False, "El numero de porciones debe ser mayor a cero"

        if not detalles_payload:
            return False, "Debes agregar al menos un ingrediente"

        detalles_normalizados = []
        for idx, item in enumerate(detalles_payload, start=1):
            id_materia = int(item.get('id_materia', 0))
            cantidad = float(item.get('cantidad', 0))

            if id_materia <= 0:
                return False, f"Ingrediente inválido en la fila {idx}"
            if cantidad <= 0:
                return False, f"La cantidad debe ser mayor a cero en la fila {idx}"

            materia = MateriaPrima.query.get(id_materia)
            if not materia:
                return False, f"Materia prima no encontrada en la fila {idx}"

            detalles_normalizados.append({'id_materia': id_materia, 'cantidad': cantidad})

        receta.rendimiento = float(rendimiento)
        receta.porciones = int(porciones)
        receta.nota = (nota or '').strip() or None
        receta.estado = bool(estado)

        RecetaDetalle.query.filter_by(id_receta=receta.id_receta).delete()

        for detalle in detalles_normalizados:
            db.session.add(RecetaDetalle(
                id_receta=receta.id_receta,
                id_materia=detalle['id_materia'],
                cantidad=detalle['cantidad'],
            ))

        db.session.commit()
        return True, "Receta actualizada correctamente"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar receta completa: {str(e)}")
        return False, str(e)
