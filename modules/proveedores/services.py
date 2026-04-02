from sqlalchemy import text
from models import db, Persona, Proveedor
from flask import current_app
import logging

logger = logging.getLogger(__name__)
def crear_proveedor(form):
    try:
        
        logger.info(f"Creando proveedor: {form.nombre.data}")
        
        db.session.execute(text("""
            CALL sp_crearProveedor(
                :nombre, :ap_p, :ap_m,
                :telefono, :correo, :direccion
            )
        """), {
            "nombre": form.nombre.data,
            "ap_p": form.apellido_p.data,
            "ap_m": form.apellido_m.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data
        })

        db.session.commit()
        logger.info(f"Proveedor creado: {form.nombre.data}")
        return True, "Proveedor creado exitosamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear proveedor: {str(e)}")
        return False, str(e)

def ver_proveedores():
    try:
        resultados = db.session.execute(text("CALL sp_verProveedores()"))
        
        proveedores= []
        for row in resultados.fetchall():
            # Convertir estado a formato booleano o string
            estado = row[6]
            # Si es 1/0, convertir a True/False; si es string, dejar como está
            if isinstance(estado, (int, bool)):
                estado_display = 'Activo' if estado else 'Inactivo'
                estado_bool = bool(estado)
            else:
                estado_display = estado
                estado_bool = estado.lower() in ['Activo', 'True', '1', 'yes']
            
            proveedores.append({'id_proveedor': row[0],
                'nombre': row[1] if len(row) > 1 else None,
                'apellido_paterno': row[2] if len(row) > 2 else None,
                'apellido_materno': row[3] if len(row) > 3 else None,
                'telefono': row[4] if len(row) > 4 else None,
                'correo': row[5] if len(row) > 5 else None,
                'estado_display': estado_display,
                'estado_bool': estado_bool
            })
        return proveedores, None
    except Exception as e:
        return None, str(e)

def filtrar_proveedores(filtro):
    try:
        result = db.session.execute(
            text("CALL sp_filtrarProveedores(:filtro)"), 
            {"filtro": filtro}
        )
        proveedores = result.fetchall()
        return proveedores, None
    except Exception as e:
        logger.error(f"Error al filtrar proveedores: {str(e)}")
        return None, str(e)
    
def desactivar_proveedor(id_proveedor):
    try:
        db.session.execute(
            text("CALL sp_eliminarProveedor(:id_proveedor)"), 
            {"id_proveedor": id_proveedor}
        )
        db.session.commit()
        logger.info(f"Proveedor {id_proveedor} desactivado")
        return True, "Proveedor desactivado exitosamente"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al desactivar proveedor: {str(e)}")
        return False, str(e)

def activar_proveedor(id_proveedor):
    try:
        db.session.execute(
            text("CALL sp_activarProveedor(:id_proveedor)"), 
            {"id_proveedor": id_proveedor}
        )
        db.session.commit()
        logger.info(f"Proveedor {id_proveedor} activado")
        return True, "Proveedor activado exitosamente"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al activar proveedor: {str(e)}")
        return False, str(e)

def obtener_proveedor(id_proveedor):
    try:
        result = db.session.execute(text("""
            SELECT 
                pr.id_proveedor,
                p.nombre,
                p.apellido_p,
                p.apellido_m,
                p.correo,
                p.telefono,
                p.direccion,
                pr.estado
            FROM proveedores pr
            LEFT JOIN personas p ON p.id_persona = pr.id_persona
            WHERE pr.id_proveedor = :id_proveedor

        """), {"id_proveedor": id_proveedor})
        
        proveedor = result.fetchone()
        if proveedor:
            return {
                'id_proveedor': proveedor[0],
                'nombre': proveedor[1],
                'apellido_paterno': proveedor[2],
                'apellido_materno': proveedor[3],
                'correo': proveedor[4],
                'telefono': proveedor[5],
                'direccion': proveedor[6],
                'estado': proveedor[7]
            }, None
        return None, "Proveedor no encontrado"
    except Exception as e:
        logger.error(f"Error al obtener proveedor: {str(e)}")
        return None, str(e)

def actualizar_proveedor(id_proveedor, form):
    try:
        db.session.execute(text("""
            CALL sp_actualizarProveedor(
                :id_proveedor, :nombre, :ap_p, :ap_m,
                :telefono, :correo, :direccion
            )   
        """), {
            "id_proveedor": id_proveedor,
            "nombre": form.get('nombre'),
            "ap_p": form.get('apellido_p'),
            "ap_m": form.get('apellido_m'),
            "telefono": form.get('telefono') or None,
            "correo": form.get('correo') or None,
            "direccion": form.get('direccion') or None
        })

        db.session.commit()
        logger.info(f"Proveedor actualizado: {form.get('nombre')}")
        return True, "Proveedor actualizado"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar proveedor: {str(e)}")
        return False, str(e)