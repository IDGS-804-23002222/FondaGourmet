from sqlalchemy import text
from werkzeug.security import generate_password_hash
from models import db, Usuario, Persona, Rol
from flask import current_app
import logging

logger = logging.getLogger(__name__)
def crear_cliente(form):
    try:
        password_hash = generate_password_hash(form.contrasena.data)

        db.session.execute(text("""
            CALL sp_crearCliente(
                :nombre, :ap_p, :ap_m,
                :telefono, :correo, :direccion,
                :username, :password
            )
        """), {
            "nombre": form.nombre.data,
            "ap_p": form.apellido_p.data,
            "ap_m": form.apellido_m.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "username": form.username.data,
            "password": password_hash
        })

        db.session.commit()
        logger.info(f"Cliente creado: {form.username.data}")
        return True, "Cliente creado exitosamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear cliente: {str(e)}")
        return False, str(e)
    
def obtener_cliente(id_usuario):
    """Obtiene un cliente con el nombre del rol"""
    try:
        result = db.session.execute(text("""
            SELECT 
                u.id_usuario, u.username, u.id_rol, u.estado, u.fecha_creacion,
                p.nombre, p.apellido_p, p.apellido_m, p.telefono, p.correo, p.direccion
            FROM Usuario u
            JOIN Persona p ON u.id_usuario = p.id_persona
            WHERE u.id_usuario = :id_usuario
        """), {"id_usuario": id_usuario})       
        cliente = result.fetchone()
        return cliente, None
    except Exception as e:

        logger.error(f"Error al obtener cliente: {str(e)}")
        return None, str(e)

def ver_mi_cuenta(id_usuario):
    try:
        result = db.session.execute(text("""
            SELECT 
                u.id_usuario,
                u.username,
                r.nombre as rol_nombre,
                p.nombre,
                p.apellido_p,
                p.apellido_m,
                p.correo,
                p.telefono,
                p.direccion
            FROM usuarios u
            INNER JOIN roles r ON u.id_rol = r.id_rol
            LEFT JOIN empleados e ON u.id_usuario = e.id_usuario
            LEFT JOIN personas p ON e.id_persona = p.id_persona
            WHERE u.id_usuario = :id_usuario
        """), {"id_usuario": id_usuario})   
        usuario = result.fetchone()
        return usuario, None
    except Exception as e:
        logger.error(f"Error al ver mi cuenta: {str(e)}")
        return None, str(e)

def actualizar_mi_cuenta(id_usuario, form):
    try:
        password_hash = generate_password_hash(form.contrasena.data) if form.contrasena.data else None

        db.session.execute(text("""
            CALL sp_actualizarMiCuenta(
                :id_usuario, :nombre, :ap_p, :ap_m,
                :telefono, :correo, :direccion,
                :username, :password    
                )
                """), {
                "id_usuario": id_usuario,
                "nombre": form.nombre.data,
                "ap_p": form.apellido_p.data,
                "ap_m": form.apellido_m.data,   
                "telefono": form.telefono.data,
                "correo": form.correo.data, 
                "direccion": form.direccion.data,
                "username": form.username.data,
                "password": password_hash
            })
        db.session.commit()
        logger.info(f"Cuenta actualizada: {form.username.data}")    
        return True, "Cuenta actualizada exitosamente"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar cuenta: {str(e)}")
        return False, str(e)    