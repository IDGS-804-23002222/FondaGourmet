from models import db, Venta, DetalleVenta, Producto, Produccion, DetalleProduccion
import logging
from sqlalchemy import text
from datetime import datetime
from flask import current_app, flash, jsonify, redirect, url_for

logger = logging.getLogger(__name__)

def obtener_ventas():
    try:
        result = db.session.execute(text("""
            SELECT 
                v.id_venta,
                v.fecha,
                v.estado,
                pr.nombre AS nombre_producto,
                pr.stock_actual,
                d.cantidad,
                v.total
            FROM ventas v
            JOIN detalle_venta d ON v.id_venta = d.id_venta
            JOIN productos pr ON d.id_producto = pr.id_producto
            ORDER BY v.fecha ASC
        """))
        
        ventas_dict = {}
        
        for row in result.mappings():
            id_venta = row['id_venta']
            
            if id_venta not in ventas_dict:
                ventas_dict[id_venta] = {
                    'id_venta': id_venta,
                    'fecha': row['fecha'],
                    'estado': row['estado'],
                    'total': row['total'],
                    'productos': [],
                    'stock_suficiente': True
                }
            
            if row['stock_actual'] < row['cantidad']:
                ventas_dict[id_venta]['stock_suficiente'] = False
                
            ventas_dict[id_venta]['productos'].append({
                'nombre': row['nombre_producto'],
                'stock_actual': row['stock_actual'],
                'cantidad': row['cantidad']
            })
            
            ventas=list(ventas_dict.values())
            return ventas, None
    except Exception as e:
        logger.error(f"Error al obtener ventas: {str(e)}")
        return None, str(e)
    
def crear_venta(id_usuario, metodo_pago, productos):
    try:
        logger.info(f"Creando venta usuario={id_usuario}")

        if not productos:
            return False, "No hay productos en la venta"

        total = 0
        necesita_produccion = False
        detalles = []

        # 🔍 VALIDACIÓN
        for item in productos:

            if not item.get("id_producto") or not item.get("cantidad"):
                return False, "Producto inválido"

            try:
                id_producto = int(item["id_producto"])
                cantidad = float(item["cantidad"])
            except:
                return False, "Datos incorrectos"

            if cantidad <= 0:
                return False, "Cantidad inválida"

            producto = Producto.query.get(id_producto)

            if not producto:
                return False, f"Producto {id_producto} no existe"

            if not producto.estado:
                return False, f"{producto.nombre} no disponible"

            subtotal = producto.precio * cantidad
            total += subtotal

            if producto.stock_actual < cantidad:
                necesita_produccion = True

            detalles.append({
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal
            })

        # 🧾 CREAR VENTA
        venta = Venta(
            id_usuario=id_usuario,
            fecha=datetime.utcnow(),
            total=total,
            metodo_pago=metodo_pago,
            estado="Pendiente" if necesita_produccion else "Completada"
        )

        db.session.add(venta)
        db.session.flush()

        # 📦 DETALLES + STOCK
        for d in detalles:
            db.session.add(DetalleVenta(
                id_venta=venta.id_venta,
                id_producto=d["producto"].id_producto,
                cantidad=d["cantidad"],
                subtotal=d["subtotal"]
            ))

            if d["producto"].stock_actual >= d["cantidad"]:
                d["producto"].stock_actual -= d["cantidad"]
            else:
                d["producto"].stock_actual = 0

        # 🏭 PRODUCCIÓN
        if necesita_produccion:
            produccion = Produccion(
                estado="Solicitada",
                fecha_solicitud=datetime.utcnow(),
                id_usuario=id_usuario
            )
            db.session.add(produccion)
            db.session.flush()

            for d in detalles:
                producto = d["producto"]

                if producto.stock_actual < d["cantidad"]:
                    faltante = d["cantidad"] - producto.stock_actual

                    db.session.add(DetalleProduccion(
                        id_produccion=produccion.id_produccion,
                        id_producto=producto.id_producto,
                        id_materia=1,  # ajustar
                        cantidad=faltante
                    ))

        db.session.commit()

        return True, "Venta registrada correctamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error crear_venta: {str(e)}")
        return False, str(e)
            
def agregar_producto_a_venta(id_venta, id_producto, cantidad):
    try:
        
        venta= Venta.query.get(id_venta)

        if not venta:
            return False, "Venta no encontrada"

        producto = Producto.query.get(id_producto)

        detalle = DetalleVenta(
            id_venta=id_venta,
            id_producto=id_producto,
            cantidad=cantidad,
            subtotal=cantidad * producto.precio
        )
        db.session.add(detalle)
        db.session.commit()
        return True, "Producto agregado a la venta"
    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
def editar_venta(id_venta, form):
    try:
        venta = Venta.query.get(id_venta)

        if not venta:
            return False, "Venta no encontrada"

        venta.fecha = form.fecha.data
        venta.total = form.total.data
        venta.metodo_pago = form.metodo_pago.data

        db.session.commit()
        return True, "Venta actualizada"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def ajustar_total_venta(id_venta):
    try:
        venta = Venta.query.get(id_venta)

        if not venta:
            return False, "Venta no encontrada"

        total_calculado = sum(d.subtotal for d in venta.detalles)
        venta.total = total_calculado

        db.session.commit()
        return True, "Total de la venta ajustado"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def disminuir_stock_productos(id_venta):
    try:
        venta = Venta.query.get(id_venta)

        if not venta:
            return False, "Venta no encontrada"

        for detalle in venta.detalles:
            producto = Producto.query.get(detalle.id_producto)
            if producto.stock_actual >= detalle.cantidad:
                producto.stock_actual -= detalle.cantidad
            else:
                return False, f"Stock insuficiente para el producto {producto.nombre}"

        db.session.commit()
        return True, "Stock de productos ajustado"
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def obtener_menu():
    """Obtiene productos activos para el menú"""
    try:
        productos = Producto.query.filter_by(estado=True).all()

        resultado = []
        for p in productos:
            resultado.append({
                "id": p.id_producto,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": p.precio,
                "imagen": p.imagen  # base64
            })

        return resultado, None

    except Exception as e:
        logger.error(f"Error al obtener menú: {str(e)}")
        return None, str(e)