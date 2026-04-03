from models import db, Usuario, Persona, Cliente, Rol
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, flash
from datetime import datetime

class AuthService:

    @staticmethod
    def validar_login(username: str, contrasena: str, correo: str = None):
        """Valida usuario + contraseña + correo (opcional)"""
        user = Usuario.query.filter_by(username=username).first()
        if not user or not user.check_password(contrasena) or not user.estado:
            current_app.logger.warning(f"Intento fallido para username: {username}")
            return None, "Usuario o contraseña incorrectos."

        # Si se pasa correo, verificamos que coincida con la persona
        if correo:
            persona = Persona.query.filter_by(correo=correo).first()
            if not persona or persona.id_persona != getattr(user.empleado or user.cliente, 'id_persona', None):
                return None, "Datos de usuario y correo no coinciden."

        current_app.logger.info(f"Login exitoso para: {username}")
        return user, None

    @staticmethod
    def crear_cliente(form):
        """Crea persona + usuario + cliente (lógica completa)"""
        try:
            # Verificar duplicados
            if Persona.query.filter(
                (Persona.correo == form.correo.data) | 
                (Persona.telefono == form.telefono.data)
            ).first():
                return False, "El correo o teléfono ya existe."

            if Usuario.query.filter_by(username=form.username.data).first():
                return False, "El nombre de usuario ya existe."

            # Crear Persona
            persona = Persona(
                nombre=form.nombre.data,
                apellido_p=form.apellido_p.data,
                apellido_m=form.apellido_m.data,
                telefono=form.telefono.data,
                correo=form.correo.data,
                direccion=form.direccion.data
            )
            db.session.add(persona)
            db.session.flush()   # para obtener el id

            # Crear Usuario (Cliente)
            rol_cliente = Rol.query.filter_by(nombre='Cliente').first()
            if not rol_cliente:
                return False, "Rol 'Cliente' no encontrado en la base de datos."

            usuario = Usuario(
                username=form.username.data,
                id_rol=rol_cliente.id_rol,
                estado=True,
                fecha_creacion=datetime.now()
            )
            usuario.set_password(form.contrasena.data)
            db.session.add(usuario)
            db.session.flush()

            # Crear Cliente
            cliente = Cliente(
                id_persona=persona.id_persona,
                id_usuario=usuario.id_usuario
            )
            db.session.add(cliente)
            db.session.commit()

            current_app.logger.info(f"Cliente creado exitosamente: {form.username.data}")
            return True, None

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creando cliente: {str(e)}")
            return False, f"Error al crear la cuenta: {str(e)}"