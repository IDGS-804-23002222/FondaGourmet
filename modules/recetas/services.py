from models import db, Receta
import logging

logger = logging.getLogger(__name__)


def obtener_recetas():
    try:
        recetas = Receta.query.order_by(Receta.fecha_creacion.desc()).all()
        resultado = []
        for receta in recetas:
            resultado.append({
                'id_receta': receta.id_receta,
                'producto_nombre': receta.producto.nombre if receta.producto else 'N/A',
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
