from sqlalchemy import text
from werkzeug.security import generate_password_hash
from models import db, Usuario, Persona, Rol

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
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
def crear_empleado(form):
    try:
        password_hash = generate_password_hash(form.contrasena.data)

        db.session.execute(text("""
            CALL sp_crearEmpleado(
                :nombre, :ap_p, :ap_m,
                :telefono, :correo, :direccion,
                :username, :password, :rol
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
            "rol": form.rol.data
        })

        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
def ver_usuarios(form):
    try:
        result = db.session.execute(text("CALL sp_verUsuarios()"))
        usuarios = result.fetchall()
        return usuarios, None
    except Exception as e:
        return None, str(e)
    

def filtrar_usuarios(form):
    try:
        result = db.session.execute(text("CALL sp_filtrarUsuarios(:filtro)"), {"filtro": form.filtro.data})
        usuarios = result.fetchall()
        return usuarios, None
    except Exception as e:
        return None, str(e)
    
def desactivar_usuario(id_usuario):
    try:
        db.session.execute(text("CALL sp_eliminarUsuario(:id_usuario)"), {"id_usuario": id_usuario})
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def activar_usuario(id_usuario):
    try:
        db.session.execute(text("CALL sp_activarUsuario(:id_usuario)"), {"id_usuario": id_usuario})
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
def obtener_usuario(id_usuario):
    try:
        result = db.session.execute(text("CALL sp_obtenerUsuario(:id_usuario)"), {"id_usuario": id_usuario})
        usuario = result.fetchone()
        return usuario, None
    except Exception as e:
        return None, str(e)
    
def actualizar_usuario(id_usuario, form):
    try:
        password_hash = generate_password_hash(form.contrasena.data) if form.contrasena.data else None

        db.session.execute(text("""
            CALL sp_actualizarUsuario(
                :id_usuario, :nombre, :ap_p, :ap_m,
                :telefono, :correo, :direccion,
                :username, :password, :rol
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
            "rol": form.rol.data
        })

        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
def ver_mi_cuenta(id_usuario):
    try:
        result = db.session.execute(text("CALL sp_verMiCuenta(:id_usuario)"), {"id_usuario": id_usuario})
        usuario = result.fetchone()
        return usuario, None
    except Exception as e:
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
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
    