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
    
def crear_empleado(form):
    try:
        password_hash = generate_password_hash(form.contrasena.data)
        
        # Obtener el rol para verificar que existe
        rol = Rol.query.filter_by(nombre=form.rol.data).first()
        if not rol:
            return False, f"Rol '{form.rol.data}' no encontrado"
        
        logger.info(f"Creando empleado: {form.username.data}, Rol: {rol.nombre} (ID: {rol.id_rol})")
        
        # Enviar el NOMBRE del rol en lugar del ID
        db.session.execute(text("""
            CALL sp_crearEmpleado(
                :nombre, :ap_p, :ap_m,
                :telefono, :correo, :direccion,
                :username, :password, :rol_nombre
            )
        """), {
            "nombre": form.nombre.data,
            "ap_p": form.apellido_p.data,
            "ap_m": form.apellido_m.data,
            "telefono": form.telefono.data,
            "correo": form.correo.data,
            "direccion": form.direccion.data,
            "username": form.username.data,
            "password": password_hash,
            "rol_nombre": rol.nombre  # Enviar el NOMBRE
        })

        db.session.commit()
        logger.info(f"Empleado creado: {form.username.data}")
        return True, "Empleado creado exitosamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear empleado: {str(e)}")
        return False, str(e)
    
def ver_usuarios():
    try:
        resultados = db.session.execute(text("CALL sp_verUsuarios()"))
        
        usuarios= []
        for row in resultados.fetchall():
            # Convertir estado a formato booleano o string
            estado = row[2]
            # Si es 1/0, convertir a True/False; si es string, dejar como está
            if isinstance(estado, (int, bool)):
                estado_display = 'Activo' if estado else 'Inactivo'
                estado_bool = bool(estado)
            else:
                estado_display = estado
                estado_bool = estado.lower() in ['Activo', 'True', '1', 'yes']
            
            usuarios.append({'id_usuario': row[0],
                'username': row[1],
                'estado_display': estado_display,
                'estado_bool': estado_bool,
                'nombre': row[3] if len(row) > 3 else None,
                'apellido_paterno': row[4] if len(row) > 4 else None,
                'apellido_materno': row[5] if len(row) > 5 else None,
                'rol_nombre': row[6] if len(row) > 6 else None,
            })
        return usuarios, None
    except Exception as e:
        return None, str(e)

def filtrar_usuarios(filtro):
    try:
        result = db.session.execute(
            text("CALL sp_filtrarUsuarios(:filtro)"), 
            {"filtro": filtro}
        )
        usuarios = result.fetchall()
        return usuarios, None
    except Exception as e:
        logger.error(f"Error al filtrar usuarios: {str(e)}")
        return None, str(e)
    
def desactivar_usuario(id_usuario):
    try:
        db.session.execute(
            text("CALL sp_eliminarUsuario(:id_usuario)"), 
            {"id_usuario": id_usuario}
        )
        db.session.commit()
        logger.info(f"Usuario {id_usuario} desactivado")
        return True, "Usuario desactivado exitosamente"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al desactivar usuario: {str(e)}")
        return False, str(e)

def activar_usuario(id_usuario):
    try:
        db.session.execute(
            text("CALL sp_activarUsuario(:id_usuario)"), 
            {"id_usuario": id_usuario}
        )
        db.session.commit()
        logger.info(f"Usuario {id_usuario} activado")
        return True, "Usuario activado exitosamente"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al activar usuario: {str(e)}")
        return False, str(e)
    
def obtener_usuario(id_usuario):
    """Obtiene un usuario con el nombre del rol"""
    try:
        result = db.session.execute(text("""
            SELECT 
                u.id_usuario,
                u.username,
                u.estado,
                r.id_rol,
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
        if usuario:
            return {
                'id_usuario': usuario[0],
                'username': usuario[1],
                'estado': usuario[2],
                'id_rol': usuario[3],
                'rol_nombre': usuario[4],
                'nombre': usuario[5],
                'apellido_paterno': usuario[6],
                'apellido_materno': usuario[7],
                'correo': usuario[8],
                'telefono': usuario[9],
                'direccion': usuario[10]
            }, None
        return None, "Usuario no encontrado"
    except Exception as e:
        logger.error(f"Error al obtener usuario: {str(e)}")
        return None, str(e)
    
def actualizar_usuario(id_usuario, form):
    try:
        password_hash = generate_password_hash(form.contrasena.data) if form.contrasena.data else None
        
        # Obtener el id_rol desde el nombre del rol
        rol = Rol.query.filter_by(nombre=form.rol.data).first()
        if not rol:
            return False, f"Rol '{form.rol.data}' no encontrado"

        logger.info(f"Actualizando usuario {id_usuario} con Rol ID: {rol.id_rol}")
        
        db.session.execute(text("""
            CALL sp_actualizarUsuario(
                :id_usuario, :nombre, :ap_p, :ap_m,
                :telefono, :correo, :direccion,
                :username, :password, :id_rol
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
            "password": password_hash,
            "id_rol": rol.id_rol  # Enviamos el ID del rol
        })

        db.session.commit()
        logger.info(f"Usuario {id_usuario} actualizado")
        return True, "Usuario actualizado exitosamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar usuario: {str(e)}")
        return False, str(e)
    
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
        return True, "Cuenta actualizada exitosamente"

    except Exception as e:
        db.session.rollback()
        return False, str(e)

# Función auxiliar para obtener todos los roles (para llenar selects)
def obtener_roles():
    """Obtiene todos los roles disponibles"""
    try:
        roles = Rol.query.all()
        return [(rol.id_rol, rol.nombre) for rol in roles], None
    except Exception as e:
        logger.error(f"Error al obtener roles: {str(e)}")
        return None, str(e)

def obtener_roles_nombres():
    """Obtiene solo los nombres de los roles"""
    try:
        roles = Rol.query.all()
        return [rol.nombre for rol in roles], None
    except Exception as e:
        logger.error(f"Error al obtener nombres de roles: {str(e)}")
        return None, str(e)