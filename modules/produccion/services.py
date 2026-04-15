from models import db, Pedido, Produccion, Compra, DetalleCompra, Producto, DetalleProduccion
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import text, func
import logging
import os
logger = logging.getLogger(__name__)


def crear_solicitud_produccion_desde_alerta(id_producto, id_usuario, cantidad=10):
    try:
        producto = Producto.query.get(id_producto)

        if not producto:
            return None, "Producto no encontrado"

        cantidad = float(cantidad or 0)
        if cantidad <= 0:
            return None, "La cantidad a producir debe ser mayor a cero"

        produccion = Produccion(
            fecha_solicitud=datetime.now(),
            fecha_necesaria=datetime.now() + timedelta(days=3),
            estado="Solicitada",
            id_usuario=id_usuario,
        )

        db.session.add(produccion)
        db.session.flush()

        db.session.add(DetalleProduccion(
            id_produccion=produccion.id_produccion,
            id_producto=producto.id_producto,
            id_materia=None,
            cantidad=cantidad
        ))

        db.session.commit()
        return produccion.id_produccion, f"Solicitud de producción creada para {producto.nombre} con {cantidad:g} unidades"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear solicitud de producción desde alerta: {str(e)}")
        return None, str(e)

def obtener_producciones():
    try:
        result = db.session.execute(text("""
            SELECT
                pr.id_produccion,
                pr.estado,
                pr.fecha_solicitud,
                pr.fecha_completada,
                pr.fecha_necesaria,
                u.username AS usuario
            FROM producciones pr
            JOIN usuarios u ON pr.id_usuario = u.id_usuario
            ORDER BY pr.fecha_necesaria ASC
        """))

        producciones = []

        for row in result.mappings():
            fecha_necesaria = row['fecha_necesaria']

            dias_restantes = None
            if fecha_necesaria:
                dias_restantes = (fecha_necesaria - datetime.now()).days

            producciones.append({
                'id_produccion': row['id_produccion'],
                'estado': row['estado'],
                'fecha_solicitud': row['fecha_solicitud'],
                'fecha_completada': row['fecha_completada'],
                'fecha_necesaria': fecha_necesaria,
                'usuario': row['usuario'],
                'dias_restantes': dias_restantes
            })

        return producciones, None

    except Exception as e:
        logger.error(f"Error al obtener producciones: {str(e)}")
        return None, str(e)
    
def completar_o_solicitar_compra(id_produccion, id_usuario):
    try:
        prod = Produccion.query.get(id_produccion)

        if not prod:
            return False, "Producción no encontrada"

        requerimientos_por_materia = {}
        
        # validar materia prima de cada detalle
        for detalle in prod.detalles:
            producto = detalle.producto
            cantidad = float(detalle.cantidad or 0)
            
            recetas = producto.recetas[0] if producto.recetas else None
            
            if not recetas:
                continue
            
            veces = cantidad / recetas.rendimiento if recetas.rendimiento > 0 else 0
            
            for r in recetas.detalles:
                materia = r.materia_prima
                requerido = r.cantidad * veces

                if not materia:
                    continue

                item = requerimientos_por_materia.setdefault(
                    materia.id_materia,
                    {
                        "materia": materia,
                        "requerido": 0.0,
                        "stock_actual": float(materia.stock_actual or 0),
                    }
                )
                item["requerido"] += float(requerido)

        compras_pendientes_por_materia = {}
        ids_materias_requeridas = list(requerimientos_por_materia.keys())

        if ids_materias_requeridas:
            pendientes = (
                db.session.query(
                    DetalleCompra.id_materia,
                    func.coalesce(func.sum(DetalleCompra.cantidad), 0)
                )
                .join(Compra, Compra.id_compra == DetalleCompra.id_compra)
                .filter(
                    Compra.estado.in_(['Solicitada', 'En Camino', 'En Proceso']),
                    DetalleCompra.id_materia.in_(ids_materias_requeridas)
                )
                .group_by(DetalleCompra.id_materia)
                .all()
            )
            compras_pendientes_por_materia = {
                id_materia: float(total_pendiente or 0)
                for id_materia, total_pendiente in pendientes
            }

        faltantes_global = []
        for id_materia, item in requerimientos_por_materia.items():
            pendiente_compra = compras_pendientes_por_materia.get(id_materia, 0.0)
            faltante = round(max(0.0, item["requerido"] - item["stock_actual"] - pendiente_compra), 2)
            if faltante > 0:
                faltantes_global.append({
                    "materia": item["materia"],
                    "faltante": faltante,
                    "stock_actual": item["stock_actual"],
                    "requerido": item["requerido"],
                    "pendiente_compra": pendiente_compra,
                })
            
        # determinar si se completa o se solicita compra
        if faltantes_global:
                        
            # generar solicitud de compra
            nueva_compra = Compra(
                fecha=datetime.now(),
                total=0,
                desde_produccion=True,
                id_proveedor=None,
                id_usuario=id_usuario
            )

            db.session.add(nueva_compra)
            db.session.flush()

            total_compra = 0

            for f in faltantes_global:
                materia = f['materia']
                faltante = f['faltante']

                subtotal = materia.precio * faltante
                total_compra += subtotal

                detalle_compra = DetalleCompra(
                    id_compra=nueva_compra.id_compra,
                    id_materia=materia.id_materia,
                    cantidad=faltante,
                    precio_u=materia.precio,
                    subtotal=subtotal
                )
                db.session.add(detalle_compra)

            nueva_compra.total = total_compra

            prod.estado = "En Proceso"
            db.session.commit()
            
            logger.info(f"Compra generada con {len(faltantes_global)} materias faltantes para producción {id_produccion}")
            return False, "Faltan ingredientes. Se generó solicitud de compra con las cantidades exactas requeridas."
            
            # si todo sale bien, se completa la producción
        for detalle in prod.detalles:
            producto = detalle.producto
            cantidad = float(detalle.cantidad or 0)
            receta = producto.recetas[0] if producto.recetas else None
            
            if receta:
                veces = cantidad / receta.rendimiento if receta.rendimiento > 0 else 0

                for r in receta.detalles:
                    materia = r.materia_prima
                    requerido = r.cantidad * veces
                    
                    materia.stock_actual -= requerido

                producto.stock_actual += cantidad
                producto.fecha_produccion = datetime.utcnow()
                producto.fecha_merma = None
            
            prod.estado = "Completada"
            prod.fecha_completada = datetime.now()
            db.session.commit()
        
        if prod.pedido:
            pedido=Pedido.query.get(prod.pedido.id_pedido)
            prod.pedido.estado = "Producido"
        
        db.session.commit()
        return True, "Producción completada y stock actualizado"

    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
def ver_orden_produccion(id_produccion):
    try:
        prod = Produccion.query.get(id_produccion)

        if not prod:
            return None, "Producción no encontrada"

        filas = []

        for detalle in prod.detalles:
            producto = detalle.producto
            cantidad = detalle.cantidad

            receta = producto.recetas[0] if producto.recetas else None

            ingredientes = []

            for r in receta.detalles:
                materia = r.materia_prima

                veces = cantidad / receta.rendimiento if receta.rendimiento > 0 else 0
                requerido = r.cantidad * veces
                stock = materia.stock_actual

                ingredientes.append({
                    "nombre": materia.nombre,
                    "requerido": round(requerido,2),
                    "stock": round(stock,2),
                    "unidad": materia.unidad_medida,
                    "faltante": stock < requerido
                })
                
            filas.append({
                "id_detalle": detalle.id_detalle,
                "producto": producto.nombre,
                "cantidad": cantidad,
                "ingredientes": ingredientes,
                "completado": False  
            })
            

        data = {
            "id_produccion": prod.id_produccion,
            "fecha": prod.fecha_solicitud,
            "fecha_completada": prod.fecha_completada,
            "estado": prod.estado,
            "filas": filas
        }

        return data, None

    except Exception as e:
        return None, str(e)
    
def validar_materia_prima_produccion(detalle):
    faltantes = []

    producto = detalle.producto
    cantidad = detalle.cantidad

    receta = producto.recetas[0] if producto.recetas else None

    if not receta:
        return []

    veces = cantidad / receta.rendimiento if receta.rendimiento > 0 else 0

    for r in receta.detalles:
        materia = r.materia_prima

        requerido = r.cantidad * veces

        if materia.stock_actual < requerido:
            faltantes.append({
                "materia": materia,
                "faltante": requerido - materia.stock_actual,
                "stock_actual": materia.stock_actual,
                "requerido": requerido
            })

    return faltantes
