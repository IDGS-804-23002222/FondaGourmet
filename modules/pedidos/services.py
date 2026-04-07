from models import db, Pedido, DetallePedido, Produccion, Producto, DetalleProduccion
from flask import current_app
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def obtener_pedidos():
    try:
        result = db.session.execute(text("""
            SELECT 
                p.id_pedido,
                p.fecha,
                p.estado,
                pr.nombre AS nombre_producto,
                pr.stock_actual,
                d.cantidad
            FROM pedidos p
            JOIN detalle_pedido d ON p.id_pedido = d.id_pedido
            JOIN productos pr ON d.id_producto = pr.id_producto
            ORDER BY p.fecha ASC
        """))

        pedidos_dict = {}

        for row in result.mappings():
            id_pedido = row['id_pedido']

            # Si el pedido no existe, lo creamos
            if id_pedido not in pedidos_dict:
                pedidos_dict[id_pedido] = {
                    'id_pedido': id_pedido,
                    'fecha': row['fecha'],
                    'estado': row['estado'],
                    'productos': [], 
                    'stock_suficiente': True
                }
                
            if row['stock_actual'] < row['cantidad']:
                pedidos_dict[id_pedido]['stock_suficiente'] = False

            # Agregamos producto al pedido
            pedidos_dict[id_pedido]['productos'].append({
                'nombre': row['nombre_producto'],
                'stock_actual': row['stock_actual'],
                'cantidad': row['cantidad']
            })

        pedidos = list(pedidos_dict.values())

        return pedidos, None

    except Exception as e:
        logger.error(f"Error al obtener pedidos: {str(e)}")
        return None, str(e)
    
def obtener_pedido(id_cliente):
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
    
def solicitar_produccion(id_pedido):
    try:
        pedido = Pedido.query.get(id_pedido)
        if not pedido:
            return False, "Pedido no encontrado"
        
        if pedido.estado != "Pendiente":
            return False, f"El pedido no se puede iniciar desde el estado '{pedido.estado}'"
        
        pedido.estado = "En proceso"
        
        db.session.commit()
        
        prod = Produccion(
            id_pedido=id_pedido,
            fecha_solicitud=pedido.fecha,
            estado="Solicitada",
            id_usuario=pedido.cliente.usuario.id_usuario
        )
        db.session.add(prod)
        
        for detalle in pedido.detalles:
            det_prod = DetalleProduccion(
                id_produccion=prod.id_produccion,
                id_producto=detalle.id_producto,
                cantidad=detalle.cantidad,
                id_materia=None
            )
            db.session.add(det_prod)
            
        db.session.commit()
            
        return True, "Pedido iniciado"
    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
def completar_pedido(id_pedido):
    try:
        pedido = Pedido.query.get(id_pedido)
        if not pedido:
            return False, "Pedido no encontrado"
        
        producto = Producto.query.get(pedido.detalles[0].id_producto) if pedido.detalles else None
        if producto and producto.stock_actual < pedido.detalles[0].cantidad:
            return False, f"Stock insuficiente para el producto '{producto.nombre}'"
        
        pedido.estado = "Completado"
        if producto:
            producto.stock_actual -= pedido.detalles[0].cantidad

        db.session.commit()
        return True, "Pedido completado"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def cancelar_pedido(id_pedido):
    try:
        pedido = Pedido.query.get(id_pedido)
        
        if not pedido:
            return False, "Pedido no encontrado"
        
        if pedido.estado == "Completado":
            return False, "No se puede cancelar un pedido completado"
        elif pedido.estado == "Cancelado":
            return False, "El pedido ya está cancelado"
        elif pedido.estado == "En proceso":
            return False, "No se puede cancelar un pedido en proceso"
        
        pedido.estado = "Cancelado"
        
        db.session.commit()
        return True, "Pedido cancelado"
    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
    from models import db, Pedido, DetallePedido, Producto, Produccion, DetalleProduccion
from datetime import datetime

def completar_o_producir(id_pedido, id_usuario):
    try:
        pedido = Pedido.query.get(id_pedido)

        if not pedido:
            return False, "Pedido no encontrado"

        necesita_produccion = False

        for detalle in pedido.detalles:
            producto = Producto.query.get(detalle.id_producto)

            if producto.stock_actual < detalle.cantidad:
                necesita_produccion = True
                break

        if not necesita_produccion:
            for detalle in pedido.detalles:
                producto = Producto.query.get(detalle.id_producto)
                producto.stock_actual -= detalle.cantidad

            pedido.estado = "Completado"
            db.session.commit()

            return True, "Pedido completado correctamente"

        produccion = Produccion(
            fecha_solicitud=datetime.now(),
            estado="Solicitada",
            id_usuario=id_usuario
        )

        db.session.add(produccion)
        db.session.flush()  # para obtener ID

        for detalle in pedido.detalles:
            db.session.add(DetalleProduccion(
                id_produccion=produccion.id_produccion,
                id_producto=detalle.id_producto,
                id_materia=None,  # si no usas materia aquí
                cantidad=detalle.cantidad
            ))

        pedido.estado = "En Proceso"
        db.session.commit()

        return True, "No hay stock suficiente. Se solicitó producción."

    except Exception as e:
        db.session.rollback()
        return False, str(e)