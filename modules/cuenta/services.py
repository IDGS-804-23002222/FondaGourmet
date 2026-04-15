from flask import flash, redirect, url_for, current_app, request, render_template
from flask_login import login_user
from models import db, Usuario
from sqlalchemy import text, or_
from werkzeug.security import generate_password_hash
from models import db, Usuario, Persona, Rol, Cliente
import logging
import uuid

logger = logging.getLogger(__name__)

def ver_perfil(id_usuario):
    try:
        result = db.session.execute(text("""
            SELECT 
    u.id_usuario,
    u.username,
    u.estado,
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
LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
LEFT JOIN personas p ON p.id_persona = COALESCE(e.id_persona, c.id_persona)
WHERE u.id_usuario = :id_usuario
        """), {"id_usuario": id_usuario})   
        usuario = result.mappings().first()
        return usuario, None
    except Exception as e:
        logger.error(f"Error al obtener perfil del usuario: {str(e)}")
        return None, str('Error al obtener perfil del usuario: ' + str(e))

def crear_cliente(form):
    try:
        correo = (form.correo.data or '').strip().lower()
        telefono = (form.telefono.data or '').strip()
        username = (form.username.data or '').strip()

        if Usuario.query.filter_by(username=username).first():
            return False, 'El nombre de usuario ya esta registrado.'

        if Persona.query.filter_by(correo=correo).first():
            return False, 'El correo ya esta registrado.'

        if Persona.query.filter_by(telefono=telefono).first():
            return False, 'El telefono ya esta registrado.'

        rol_cliente = Rol.query.filter_by(nombre='Cliente').first()
        if not rol_cliente:
            return False, 'No existe el rol Cliente configurado en el sistema.'

        persona = Persona(
            nombre=(form.nombre.data or '').strip(),
            apellido_p=(form.apellido_p.data or '').strip(),
            apellido_m=(form.apellido_m.data or '').strip() or None,
            telefono=telefono,
            correo=correo,
            direccion=(form.direccion.data or '').strip() or None,
        )
        db.session.add(persona)
        db.session.flush()

        usuario = Usuario(
            username=username,
            contrasena=generate_password_hash(form.contrasena.data),
            estado=True,
            fs_uniquifier=str(uuid.uuid4()),
            id_rol=rol_cliente.id_rol,
        )
        db.session.add(usuario)
        db.session.flush()

        cliente = Cliente(
            id_usuario=usuario.id_usuario,
            id_persona=persona.id_persona,
        )
        db.session.add(cliente)

        db.session.commit()
        logger.info(f"Cliente creado: {form.username.data}")
        return True, "Cliente creado exitosamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear cliente: {str(e)}")
        return False, str('Error al crear cliente: ' + str(e))
    
def actualizar_mi_cuenta(id_usuario, form):
    try:
        password_hash = None

        if form.contrasena.data:
            password_hash = generate_password_hash(form.contrasena.data)

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
        return True, "Perfil actualizado correctamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar cuenta: {str(e)}")
        return False, str(e)

    
def validar_datos(form, id_usuario=None):
    username = form.username.data.strip()
    correo = form.correo.data.strip().lower()
    telefono = form.telefono.data.strip()

    usuario_existente = Usuario.query.filter(
        Usuario.id_usuario != (id_usuario or 0),
        Usuario.username == username
    ).first()

    persona_existente = Persona.query.filter(
        or_(
            Persona.correo == correo,
            Persona.telefono == telefono
        )
    ).first()
    
    if usuario_existente:
        return False, "El nombre de usuario ya está en uso."

    if persona_existente:
        if persona_existente.correo == correo:
            return False, "El correo electrónico ya está registrado."
        if persona_existente.telefono == telefono:
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
LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
LEFT JOIN personas p ON p.id_persona = COALESCE(e.id_persona, c.id_persona)
WHERE u.id_usuario = :id_usuario
        """), {"id_usuario": id_usuario})
        
        usuario = result.mappings().first()
        return usuario, None
    except Exception as e:
        logger.error(f"Error al cargar datos del usuario: {str(e)}")
        return None, str("Error al cargar datos del usuario: " + str(e))