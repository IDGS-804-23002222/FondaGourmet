from models import db, Pedido, DetallePedido
from flask import current_app
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def obtener_pedidos(id_cliente):
    try:
        logger.info(f"Obteniendo pedidos para cliente: {id_cliente}")
        
        if not id_cliente:
            logger.warning("ID de cliente no proporcionado")
            return None, "ID de cliente no proporcionado."
        
        pedidos = Pedido.query.filter_by(id_cliente=id_cliente).order_by(Pedido.fecha.desc()).all()
        resultado = []
        for p in pedidos:
            resultado.append({
                'id': p.id_pedido,
                'fecha': p.fecha,
                'total': p.total,
                'estado': p.estado
            })
        logger.info(f"Pedidos obtenidos: {len(resultado)} para cliente: {id_cliente}")
        return resultado, None
    except Exception as e:
        logger.error(f"Error al obtener pedidos: {str(e)}")
        return None, str(e)
    
def obtener_detalles_pedido(id_pedido):
    try:
        logger.info(f"Obteniendo detalles para pedido: {id_pedido}")
        detalles = DetallePedido.query.filter_by(id_pedido=id_pedido).all()
        resultado = []
        for d in detalles:
            resultado.append({
                'id': d.id_detalle,
                'id_pedido': d.id_pedido,
                'id_producto': d.id_producto,
                'cantidad': d.cantidad
            })
        logger.info(f"Detalles obtenidos para pedido {id_pedido}: {len(resultado)}")
        return resultado, None
    except Exception as e:
        logger.error(f"Error al obtener detalles del pedido: {str(e)}")
        return None, str(e)