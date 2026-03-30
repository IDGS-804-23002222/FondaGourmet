from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, RadioField, BooleanField, DateField, SelectField, EmailField, FloatField, PasswordField
from wtforms import validators

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario',[
        validators.DataRequired(message="El nombre de usuario es obligatorio."),
    ])
    
    contrasena = PasswordField('Contraseña', [
        validators.DataRequired(message="La contraseña es obligatoria.")
        ])
    
    captcha = StringField('Captcha', [
        validators.DataRequired(message="El captcha es obligatorio.")
        ])
   
    submit = SubmitField('Iniciar sesión')

class RegistroUsuarioForm(FlaskForm):
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
    
    username = StringField('Nombre de usuario', [
        validators.DataRequired(message="El nombre de usuario es obligatorio."),
        validators.Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")
        ])
    
    contrasena = PasswordField('Contraseña', [
        validators.DataRequired(message="La contraseña es obligatoria."),
        validators.Length(min=8, message="La contraseña debe tener al menos 8 caracteres.")
        ])
    
    confirmar_contrasena = PasswordField('Confirmar contraseña', [
        validators.DataRequired(message="La confirmación de contraseña es obligatoria."),
        validators.EqualTo('contrasena', message="Las contraseñas deben coincidir.")
    ])
    
    rol= SelectField('Rol', choices=[
        ('Cocinero', 'Cocinero'),   
        ('Administrador', 'Administrador'),
        ('Cajero', 'Cajero'),
        ('Dueño', 'Dueño'),
        ('Cliente', 'Cliente')
        ], validators=[
            validators.DataRequired(message="Seleccione un rol."),
            validators.AnyOf(values=['Cocinero', 'Administrador', 'Cajero', 'Dueño', 'Cliente'], message="Seleccione un rol válido.")
        ])
    
    submit = SubmitField('Crear usuario')

class RegistroClienteForm(FlaskForm):
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
    
    username = StringField('Nombre de usuario', [
        validators.DataRequired(message="El nombre de usuario es obligatorio."),
        validators.Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")
        ])
    
    contrasena = PasswordField('Contraseña', [
        validators.DataRequired(message="La contraseña es obligatoria."),
        validators.Length(min=8, message="La contraseña debe tener al menos 8 caracteres.")
        ])
    
    confirmar_contrasena = PasswordField('Confirmar contraseña', [
        validators.DataRequired(message="La confirmación de contraseña es obligatoria."),
        validators.EqualTo('contrasena', message="Las contraseñas deben coincidir.")
    ])
    
    submit = SubmitField('Crear cuenta')

class UsuarioForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(message="El nombre de usuario es obligatorio."),
        validators.Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")
        ])
    
    contrasena = PasswordField('Contraseña', [
        validators.DataRequired(message="La contraseña es obligatoria."),
        validators.Length(min=6, message="La contraseña debe tener al menos 6 caracteres.")
        ])
    
    rol = SelectField('Rol', choices=[
        ('Cocinero', 'Cocinero'), 
        ('Administrador', 'Administrador'),
        ('Cajero', 'Cajero'),
        ('Dueño', 'Dueño'),
        ('Cliente', 'Cliente')
        ], validators=[
            validators.DataRequired(message="Seleccione un rol."),
            validators.AnyOf(values=['Cocinero', 'Administrador', 'Cajero', 'Dueño', 'Cliente'], message="Seleccione un rol válido.")
        ])
    
class PersonaForm(FlaskForm):
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

class CategoriaForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.DataRequired(message='El nombre es obligatorio'),
        validators.length(min=2,max=100, message='El nombre debe tener entre 2 y 100 caracteres')
    ])
    
    descripcion = StringField('Descripcion', [
        validators.DataRequired(message='La descripcion es obligatoria')
    ])

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre',[
        validators.DataRequired(message='El nombre es obligatorio'),
        validators.length(min=2,max=100, message='El nombre debe tener entre 2 y 100 caracteres')
    ])
    
    descripcion = StringField('Descripcion', [
        validators.DataRequired(message='La descripcion es obligatoria')
    ])

    precio = FloatField('Precio', [
        validators.DataRequired(message='El precio es obligatorio')
    ])
    
    stock_actual = FloatField ('Stock_actual')