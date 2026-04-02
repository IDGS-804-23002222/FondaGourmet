from flask import flash, redirect, url_for, current_app, request, render_template
from flask_login import login_user
from models import db, Usuario
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from models import db, Usuario, Persona, Rol
import logging

logger = logging.getLogger(__name__)

def ver_perfil(id_usuario):
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
            LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
            WHERE u.id_usuario = :id_usuario
        """), {"id_usuario": id_usuario})   
        usuario = result.mappings().first()
        return usuario, None
    except Exception as e:
        logger.error(f"Error al obtener perfil del usuario: {str(e)}")
        return None, str('Error al obtener perfil del usuario: ' + str(e))

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
        return False, str('Error al crear cliente: ' + str(e))
    
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
                "nombre": form.get('nombre') or None,
                "ap_p": form.get('apellido_p') or None,
                "ap_m": form.get('apellido_m') or None,
                "telefono": form.get('telefono') or None,
                "correo": form.get('correo') or None,
                "direccion": form.get('direccion') or None,
                "username": form.get('username') or None,
                "password": password_hash or None
            })
        
        db.session.commit()
        logger.info(f"Cuenta actualizada: {form.get('username').data}")    
        return True, "Cuenta actualizada exitosamente"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar cuenta: {str(e)}")
        return False, str("Error al actualizar cuenta: " + str(e))    
    
def validar_datos(form, id_usuario=None):
    username = form.username.data.strip()
    correo = form.correo.data.strip().lower()
    telefono = form.telefono.data.strip()

    usuario_existente = Usuario.query.filter(
        or_(
            Usuario.username == username,
            Usuario.correo == correo,
            Usuario.telefono == telefono
        )
    ).first()
    
    if usuario_existente:
        if id_usuario and usuario_existente.id_usuario == id_usuario:
            return True, None 
        if usuario_existente.username == username:
            return False, "El nombre de usuario ya está en uso."
        
        if usuario_existente.correo == correo:
            return False, "El correo electrónico ya está registrado."
        
        if usuario_existente.telefono == telefono:
            return False, "El número de teléfono ya está registrado."

    return True, None

def cargar_datos_usuario(id_usuario, form):
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
            LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
            WHERE u.id_usuario = :id_usuario
        """), {"id_usuario": id_usuario})
        
        usuario = result.mappings().first()
        return usuario, None
    except Exception as e:
        logger.error(f"Error al cargar datos del usuario: {str(e)}")
        return None, str("Error al cargar datos del usuario: " + str(e))