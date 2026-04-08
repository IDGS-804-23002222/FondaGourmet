from models import db, Compra, DetalleCompra, MateriaPrima
from flask import current_app
from sqlalchemy import text
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def obtener_compras():
    try:
        result = db.session.execute(text("""
    SELECT 
        c.id_compra,
        c.fecha,
        c.fecha_entrega,
        c.estado,
        m.nombre AS nombre_materia,
        d.cantidad,
        m.stock_actual,
        d.cantidad
    FROM compras c
    JOIN detalle_compra d ON c.id_compra = d.id_compra
    JOIN materias_primas m ON d.id_materia = m.id_materia
    WHERE c.estado IN ('Solicitada', 'En Proceso', 'Completada')
    ORDER BY c.fecha ASC
"""))

        compras_dict = {}

        for row in result.mappings():
            id_compra = row['id_compra']

            # Si la compra no existe, la creamos
            if id_compra not in compras_dict:
                compras_dict[id_compra] = {
                    'id_compra': id_compra,
                    'fecha': row['fecha'],
                    'fecha_entrega': row['fecha_entrega'],
                    'estado': row['estado'],
                    'materias_primas': []
                    }
                
            if row['stock_actual'] < row['cantidad']:
                compras_dict[id_compra]['stock_suficiente'] = False

            # Agregamos materia prima a la compra
            compras_dict[id_compra]['materias_primas'].append({
                'nombre': row['nombre_materia'],
                'stock_actual': row['stock_actual'],
                'cantidad': row['cantidad']
            })

        compras = list(compras_dict.values())

        return compras, None

    except Exception as e:
        logger.error(f"Error al obtener compras: {str(e)}")
        return None, str(e)
    
def obtener_compra(id_compra):
    try:
        compra = Compra.query.get(id_compra)

        if not compra:
            return None, "Compra no encontrada"

        data = {
            "id": compra.id_compra,
            "fecha": compra.fecha,
            "fecha_entrega": compra.fecha_entrega,
            "estado": compra.estado,
            "metodo_pago": compra.metodo_pago,
            "total": compra.total,
            "materias_primas": []
        }

        for d in compra.detalles:
            materia = d.materia_prima

            data["materias_primas"].append({
                "id_detalle": d.id_detalle,
                "id_materia": materia.id_materia,
                "nombre": materia.nombre,
                "cantidad": d.cantidad,
                "precio_unitario": d.precio_u,  # 🔥 CORRECTO
                "stock_actual": materia.stock_actual
            })

        return data, None

    except Exception as e:
        return None, str(e)
        
def completar_compra(id_compra):
    try:
        compra = Compra.query.get(id_compra)

        if not compra:
            return False, "Compra no encontrada"

        if compra.estado == "Completada":
            return False, "Ya fue completada"

        for detalle in compra.detalles:
            materia = detalle.materia_prima
            materia.stock_actual += detalle.cantidad

        compra.estado = "Completada"
        compra.fecha_entrega = datetime.now()

        db.session.commit()

        return True, "Compra completada correctamente"

    except Exception as e:
        db.session.rollback()
        return False, str(e)