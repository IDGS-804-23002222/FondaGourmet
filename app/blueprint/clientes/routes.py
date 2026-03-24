from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from forms import ClienteForm
from app.extensions import db, app, user_datastore
from app.models import Usuario, Persona, Cliente
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required
from flask_security.utils import login_user, logout_user

empleados_bp = Blueprint('empleados', __name__)

@empleados_bp.route('/')
@login_required
def index():
    empleados = Empleado.query.join(Persona).filter(
        Persona.estado == True,
        Usuario.estado == True
    ).all()
    return render_template('empleados/listEmpleados.html', empleados=empleados)

@empleados_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar():
    form = EmpleadoForm()
     
    if request.method == 'POST' and form.validate_on_submit():
        try:
            existePersona = Persona.query.filter((Persona.correo == form.correo.data) | (Persona.telefono == form.telefono.data)).first()
            existeUsuario = Usuario.query.filter_by(username=form.username.data).first()
            
            if existePersona:
                flash('El correo o teléfono ya existe. Por favor, elija otro.', 'danger')
                return render_template('empleados/registrarEmpleado.html', form=form)
            
            if existeUsuario:
                flash('El nombre de usuario ya existe. Por favor, elija otro.', 'danger')
                return render_template('empleados/registrarEmpleado.html', form=form)
            
            # Crear la persona
            persona = Persona(
                nombre=form.nombre.data,
                apellido_p=form.apellido_p.data,
                apellido_m=form.apellido_m.data,
                telefono=form.telefono.data,
                correo=form.correo.data,
                direccion=form.direccion.data
            )
             
            db.session.add(persona)
            db.session.flush()
            
            # Crear el usuario
            usuario = Usuario(
                username=form.username.data,
                contrasena=generate_password_hash(form.contrasena.data),
                id_rol=form.rol.data
            )
              
            db.session.add(usuario)
            db.session.flush()
            
            # Crear el empleado
            empleado = Empleado(
                id_usuario=usuario.id_usuario,
                id_persona=persona.id_persona
            )
            db.session.add(empleado)
            db.session.commit()
            
            flash('Empleado registrado exitosamente.', 'success')
            return redirect(url_for('empleados.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el empleado: {str(e)}', 'danger')
    
    return render_template('empleados/registrarEmpleado.html', form=form)

@empleados_bp.route('/editar/<int:id_empleado>', methods=['GET', 'POST'])
@login_required
def editar(id_empleado):
    empleado = Empleado.query.get_or_404(id_empleado)
    
    form = EmpleadoForm(obj=empleado.persona)
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            existePersona = Persona.query.filter((Persona.correo == form.correo.data) | (Persona.telefono == form.telefono.data), Persona.id_persona != empleado.id_persona).first()
            existeUsuario = Usuario.query.filter(Usuario.username == form.username.data, Usuario.id_usuario != empleado.id_usuario).first()
            
            if existePersona:
                flash('El correo o teléfono ya existe. Por favor, elija otro.', 'danger')
                return render_template('empleados/editarEmpleado.html', form=form, id_empleado=id_empleado)
            
            if existeUsuario:
                flash('El nombre de usuario ya existe. Por favor, elija otro.', 'danger')
                return render_template('empleados/editarEmpleado.html', form=form, id_empleado=id_empleado)
            
            # Actualizar la persona
            empleado.persona.nombre = form.nombre.data
            empleado.persona.apellido_p = form.apellido_p.data
            empleado.persona.apellido_m = form.apellido_m.data
            empleado.persona.telefono = form.telefono.data
            empleado.persona.correo = form.correo.data
            empleado.persona.direccion = form.direccion.data
            
            # Actualizar el usuario
            empleado.usuario.username = form.username.data
            if form.contrasena.data:
                empleado.usuario.contrasena = generate_password_hash(form.contrasena.data)
            empleado.usuario.id_rol = form.rol.data
            
            db.session.add(empleado.persona)
            db.session.add(empleado.usuario)
            db.session.add(empleado)
            db.session.commit()
            flash('Empleado actualizado exitosamente.', 'success')
            return redirect(url_for('empleados.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el empleado: {str(e)}', 'danger')
    
    return render_template('empleados/editarEmpleado.html', form=form, id_empleado=id_empleado)

@empleados_bp.route('/eliminar/<int:id_empleado>', methods=['POST'])
@login_required
def eliminar(id_empleado):
    empleado = Empleado.query.get_or_404(id_empleado)
    
    try:
        #Eliminación lógica
        empleado.persona.estado = False
        empleado.usuario.estado = False

        db.session.commit()
        flash('Empleado desactivado correctamente.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('empleados.index'))

@empleados_bp.route('/activar/<int:id_empleado>', methods=['POST'])
@login_required
def activar(id_empleado):
    empleado = Empleado.query.get_or_404(id_empleado)
    
    try:
        #Activación lógica
        empleado.persona.estado = True
        empleado.usuario.estado = True

        db.session.commit()
        flash('Empleado activado correctamente.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('empleados.index'))

@empleados_bp.route('/detalles/<int:id_empleado>', methods=['GET'])
@login_required
def detalles(id_empleado):
    empleado = Empleado.query.get_or_404(id_empleado)
    return render_template('empleados/detallesEmpleado.html', empleado=empleado)