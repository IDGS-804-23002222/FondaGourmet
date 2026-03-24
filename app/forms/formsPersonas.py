from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, RadioField, BooleanField, DateField, SelectField, EmailField
from wtforms import validators

class EmpleadoForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.DataRequired(message="El nombre es obligatorio."),
        validators.Length(min=2, max=50, message="El nombre debe tener entre 2 y 50 caracteres.")
        ])
    
    apellido_p = StringField('Apellido Paterno', [
        validators.DataRequired(message="El apellido es obligatorio."),
        validators.Length(min=2, max=50, message="El apellido debe tener entre 2 y 50 caracteres.")
        ])
    
    apellido_m = StringField('Apellido Materno', [
        validators.Length(min=2, max=50, message="El apellido debe tener entre 2 y 50 caracteres.")
        ])
    
    telefono = StringField('Teléfono', [
        validators.DataRequired(message="El teléfono es obligatorio."),
        validators.Regexp(r'^\d{10}$', message="El teléfono debe tener 10 dígitos.")
        ])
    
    correo = EmailField('Correo', [
        validators.DataRequired(message="El correo es obligatorio."),
        validators.Email(message="Ingrese un correo electrónico válido."),
        validators.Length(min=5, max=100, message="El correo debe tener entre 5 y 100 caracteres."),
        validators.Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message="El correo debe tener un formato válido.")
        ])
    
    direccion = StringField('Dirección', [
        validators.Length(min=5, max=100, message="La dirección debe tener entre 5 y 100 caracteres.")
        ])
     
    username = StringField('Username', [
        validators.DataRequired(message="El nombre de usuario es obligatorio."),
        validators.Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")
        ])
    
    contrasena = StringField('Contraseña', [
        validators.DataRequired(message="La contraseña es obligatoria."),
        validators.Length(min=6, message="La contraseña debe tener al menos 6 caracteres.")
        ])
    
    rol = SelectField('Rol', choices=[
        ('Cocinero', 'Cocinero'), 
        ('Administrador', 'Administrador'),
        ('Cajero', 'Cajero'),
        ('Dueño', 'Dueño')
        ], validators=[
            validators.DataRequired(message="Seleccione un rol."),
            validators.AnyOf(values=['Cocinero', 'Administrador', 'Cajero', 'Dueño'], message="Seleccione un rol válido.")
        ])

    submit = SubmitField('Registrar Empleado')
    
class ProveedorForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.DataRequired(message="El nombre es obligatorio."),
        validators.Length(min=2, max=50, message="El nombre debe tener entre 2 y 50 caracteres.")
        ])
    
    apellido_p = StringField('Apellido Paterno', [
        validators.DataRequired(message="El apellido es obligatorio."),
        validators.Length(min=2, max=50, message="El apellido debe tener entre 2 y 50 caracteres.")
        ])
    
    apellido_m = StringField('Apellido Materno', [
        validators.Length(min=2, max=50, message="El apellido debe tener entre 2 y 50 caracteres.")
        ])
    
    telefono = StringField('Teléfono', [
        validators.DataRequired(message="El teléfono es obligatorio."),
        validators.Regexp(r'^\d{10}$', message="El teléfono debe tener 10 dígitos.")
        ])
    
    correo = EmailField('Correo', [
        validators.DataRequired(message="El correo es obligatorio."),
        validators.Email(message="Ingrese un correo electrónico válido."),
        validators.Length(min=5, max=100, message="El correo debe tener entre 5 y 100 caracteres."),
        validators.Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message="El correo debe tener un formato válido.")
        ])
    
    direccion = StringField('Dirección', [
        validators.Length(min=5, max=100, message="La dirección debe tener entre 5 y 100 caracteres.")
        ])

    submit = SubmitField('Registrar Proveedor')
    
class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.DataRequired(message="El nombre es obligatorio."),
        validators.Length(min=2, max=50, message="El nombre debe tener entre 2 y 50 caracteres.")
        ])
    
    apellido_p = StringField('Apellido Paterno', [
        validators.DataRequired(message="El apellido es obligatorio."),
        validators.Length(min=2, max=50, message="El apellido debe tener entre 2 y 50 caracteres.")
        ])
    
    apellido_m = StringField('Apellido Materno', [
        validators.Length(min=2, max=50, message="El apellido debe tener entre 2 y 50 caracteres.")
        ])
    
    telefono = StringField('Teléfono', [
        validators.DataRequired(message="El teléfono es obligatorio."),
        validators.Regexp(r'^\d{10}$', message="El teléfono debe tener 10 dígitos.")
        ])
    
    correo = EmailField('Correo', [
        validators.DataRequired(message="El correo es obligatorio."),
        validators.Email(message="Ingrese un correo electrónico válido."),
        validators.Length(min=5, max=100, message="El correo debe tener entre 5 y 100 caracteres."),
        validators.Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message="El correo debe tener un formato válido.")
        ])
    
    direccion = StringField('Dirección', [
        validators.Length(min=5, max=100, message="La dirección debe tener entre 5 y 100 caracteres.")
        ])
    
    username = StringField('Username', [
        validators.DataRequired(message="El nombre de usuario es obligatorio."),
        validators.Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")
        ])
    
    contrasena = StringField('Contraseña', [
        validators.DataRequired(message="La contraseña es obligatoria."),
        validators.Length(min=6, message="La contraseña debe tener al menos 6 caracteres.")
        ])
    
    rol=SelectField('Rol', choices=[
        ('Cliente', 'Cliente')
        ], validators=[
            validators.DataRequired(message="Seleccione un rol."),
            validators.AnyOf(values=['Cliente'], message="Seleccione un rol válido.")
        ])

    submit = SubmitField('Registrar Cliente')