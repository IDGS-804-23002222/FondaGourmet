from models import db, Pedido, DetallePedido, Produccion, Producto, DetalleProduccion, PedidoMeta
from flask import current_app
from sqlalchemy import text
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def crear_pedido_manual(id_cliente, productos, metodo_pago, id_usuario):
    try:
        if not id_cliente:
            return False, "Debes seleccionar un cliente"

        if not productos:
            return False, "Debes agregar al menos un producto"

        if metodo_pago not in ('Efectivo', 'Tarjeta', 'Transferencia'):
            return False, "Selecciona un método de pago válido"

        detalles = []
        total = 0

        for item in productos:
            id_producto = item.get('id_producto')
            cantidad = item.get('cantidad')

            if not id_producto or not cantidad:
                return False, "Cada renglón debe tener producto y cantidad"

            try:
                id_producto = int(id_producto)
                cantidad = int(cantidad)
            except (TypeError, ValueError):
                return False, "Los datos del pedido son inválidos"

            if cantidad <= 0:
                return False, "La cantidad debe ser mayor a cero"

            producto = Producto.query.get(id_producto)
            if not producto or not producto.estado:
                return False, f"Producto inválido: {id_producto}"

            subtotal = float(producto.precio) * cantidad
            total += subtotal

            detalles.append({
                'id_producto': id_producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })

        pedido = Pedido(
            id_cliente=int(id_cliente),
            total=total,
            fecha=datetime.utcnow(),
            fecha_entrega=None,
            estado='Pendiente'
        )

        db.session.add(pedido)
        db.session.flush()

        for d in detalles:
            db.session.add(DetallePedido(
                id_pedido=pedido.id_pedido,
                id_producto=d['id_producto'],
                cantidad=d['cantidad'],
                subtotal=d['subtotal']
            ))

        db.session.add(PedidoMeta(
            id_pedido=pedido.id_pedido,
            metodo_pago=metodo_pago,
            id_usuario=id_usuario,
        ))

        db.session.commit()
        return True, "Pedido creado correctamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear pedido manual: {str(e)}")
        return False, str(e)

def obtener_pedidos():
    try:
        result = db.session.execute(text("""
    SELECT
        p.id_pedido,
        p.fecha,
        p.fecha_entrega,
        p.estado,
        pm.metodo_pago,
        ru.username AS usuario_responsable,
        pr.nombre AS nombre_producto,
        pr.stock_actual,
        d.cantidad
    FROM pedidos p
    LEFT JOIN pedidos_meta pm ON pm.id_pedido = p.id_pedido
    LEFT JOIN usuarios ru ON ru.id_usuario = pm.id_usuario
    JOIN detalle_pedido d ON p.id_pedido = d.id_pedido
    JOIN productos pr ON d.id_producto = pr.id_producto
    WHERE p.estado IN ('Pendiente', 'En Proceso', 'Completado', 'Producido')
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
                    'fecha_entrega': row['fecha_entrega'],
                    'estado': row['estado'],
                    'metodo_pago': row['metodo_pago'] or 'N/D',
                    'usuario_responsable': row['usuario_responsable'] or 'N/D',
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
            fecha_estimada = p.fecha + timedelta(days=3) if p.fecha else None
            
            resultado.append({
                'id': p.id_pedido,
                'fecha': p.fecha,
                'fecha_estimada': fecha_estimada,
                'fecha_entrega': p.fecha_entrega,
                'total': p.total,
                'requiere_produccion': p.requiere_produccion,
                'estado': p.estado,
                'metodo_pago': p.meta_pedido.metodo_pago if p.meta_pedido else 'N/D',
                'usuario_responsable': p.meta_pedido.usuario.username if p.meta_pedido and p.meta_pedido.usuario else 'N/D',
                # Pre-format the dates for the template (safest approach)
                'fecha_str': p.fecha.strftime('%d/%m/%Y') if p.fecha else '',
                'fecha_entrega_str': p.fecha_entrega.strftime('%d/%m/%Y') if p.fecha_entrega else '',
                'fecha_estimada_str': fecha_estimada.strftime('%d/%m/%Y') if fecha_estimada else ''
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
        
        estado = (pedido.estado or "").strip().lower()

        if estado == "completado":
            return False, "No se puede cancelar un pedido completado"
        elif estado == "cancelado":
            return False, "El pedido ya está cancelado"
        elif estado in ("en proceso", "producido"):
            return False, "No se puede cancelar un pedido en proceso"
        elif estado not in ("pendiente", "solicitado"):
            return False, "Solo se pueden cancelar pedidos solicitados"
        
        pedido.estado = "Cancelado"
        
        db.session.commit()
        return True, "Pedido cancelado"
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def editar_pedido_propio(id_pedido, id_cliente, productos, metodo_pago, id_usuario):
    try:
        pedido = Pedido.query.get(id_pedido)

        if not pedido:
            return False, "Pedido no encontrado"

        if pedido.id_cliente != id_cliente:
            return False, "No tienes permiso para editar este pedido"

        if pedido.estado != 'Pendiente':
            return False, "Solo puedes editar pedidos pendientes"

        if metodo_pago not in ('Efectivo', 'Tarjeta', 'Transferencia'):
            return False, "Selecciona un método de pago válido"

        detalles = []
        total = 0

        for item in productos:
            id_producto = item.get('id_producto')
            cantidad = item.get('cantidad')

            if not id_producto or not cantidad:
                return False, "Cada renglón debe tener producto y cantidad"

            try:
                id_producto = int(id_producto)
                cantidad = int(cantidad)
            except (TypeError, ValueError):
                return False, "Los datos del pedido son inválidos"

            if cantidad <= 0:
                return False, "La cantidad debe ser mayor a cero"

            producto = Producto.query.get(id_producto)
            if not producto or not producto.estado:
                return False, f"Producto inválido: {id_producto}"

            subtotal = float(producto.precio) * cantidad
            total += subtotal

            detalles.append({
                'id_producto': id_producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
            })

        if not detalles:
            return False, "Debes agregar al menos un producto"

        DetallePedido.query.filter_by(id_pedido=pedido.id_pedido).delete()

        for d in detalles:
            db.session.add(DetallePedido(
                id_pedido=pedido.id_pedido,
                id_producto=d['id_producto'],
                cantidad=d['cantidad'],
                subtotal=d['subtotal']
            ))

        meta = PedidoMeta.query.get(pedido.id_pedido)
        if not meta:
            meta = PedidoMeta(id_pedido=pedido.id_pedido, metodo_pago=metodo_pago, id_usuario=id_usuario)
            db.session.add(meta)
        else:
            meta.metodo_pago = metodo_pago
            meta.id_usuario = id_usuario

        pedido.total = total
        db.session.commit()

        return True, "Pedido actualizado correctamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al editar pedido propio: {str(e)}")
        return False, str(e)

def completar_o_producir(id_pedido, id_usuario, fecha_necesaria=None):
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

        # 🟢 CASO 1: NO necesita producción
        if not necesita_produccion:
            for detalle in pedido.detalles:
                producto = Producto.query.get(detalle.id_producto)
                producto.stock_actual -= detalle.cantidad

            pedido.estado = "Completado"
            pedido.fecha_entrega = datetime.now()
            pedido.requiere_produccion = False  # 🔥 CLAVE

            db.session.commit()

            return True, "Pedido completado sin producción"

        # 🔴 CASO 2: SÍ necesita producción
        if not fecha_necesaria:
            return False, "Debes indicar la fecha en que se necesita la producción"

        try:
            fecha_necesaria_dt = datetime.strptime(fecha_necesaria, '%Y-%m-%d')
        except ValueError:
            return False, "Fecha de producción inválida"

        if fecha_necesaria_dt.date() < datetime.now().date():
            return False, "La fecha necesaria no puede ser menor a hoy"

        produccion = Produccion(
            fecha_solicitud=datetime.now(),
            estado="Solicitada",
            fecha_necesaria=fecha_necesaria_dt,
            id_usuario=id_usuario,
            id_pedido=id_pedido
        )

        db.session.add(produccion)
        db.session.flush()

        for detalle in pedido.detalles:
            db.session.add(DetalleProduccion(
                id_produccion=produccion.id_produccion,
                id_producto=detalle.id_producto,
                id_materia=None,
                cantidad=detalle.cantidad
            ))

        pedido.estado = "En Proceso"
        pedido.requiere_produccion = True  # 🔥 CLAVE

        db.session.commit()

        return True, "Se envió a producción"

    except Exception as e:
        db.session.rollback()
        return False, str(e)