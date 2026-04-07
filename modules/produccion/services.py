from models import db, Pedido, Produccion
from datetime import datetime
from flask import current_app
from sqlalchemy import text
import logging
import os
logger = logging.getLogger(__name__)

# Historial de producciones
def obtener_producciones():
    try:
        result = db.session.execute(text("""
            SELECT
                pr.id_produccion,
                pr.estado,
                pr.fecha_solicitud,
                pr.fecha_completada,
                u.username AS usuario
            FROM producciones pr
            JOIN usuarios u ON pr.id_usuario = u.id_usuario
            ORDER BY pr.fecha_solicitud DESC
        """))
        
        producciones = result.fetchall()
        return producciones, None
    except Exception as e:
        logger.error(f"Error al obtener producciones: {str(e)}")
        return None, str(e) 
    
def crear_produccion(id_pedido):
    try:
        pedido = Pedido.query.get(id_pedido)

        if not pedido:
            return False, "Pedido no encontrado"

        prod = Produccion(
            id_pedido=id_pedido,
            estado="solicitada",
            fecha_solicitud=datetime.utcnow()
        )

        db.session.add(prod)
        db.session.commit()

        return True, "Producción creada"
    except Exception as e:
        db.session.rollback()
        return False, str(e)


# 🔹 Cambiar estado
def cambiar_estado_produccion(id, nuevo_estado):
    try:
        prod = Produccion.query.get(id)

        if not prod:
            return False, "No encontrado"

        prod.estado = nuevo_estado

        if nuevo_estado == "en_proceso":
            prod.fecha_produccion = datetime.utcnow()
        elif nuevo_estado == "completada":
            prod.fecha_completada = datetime.utcnow()

        db.session.commit()
        return True, "Estado actualizado"

    except Exception as e:
        db.session.rollback()
        return False, str(e)

def iniciar_produccion(id):
    return cambiar_estado_produccion(id, "en_proceso")

def completar_produccion(id):
    return cambiar_estado_produccion(id, "completada")

def cancelar_produccion(id):
    return cambiar_estado_produccion(id, "cancelada")
