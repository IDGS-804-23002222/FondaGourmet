from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, RadioField, BooleanField, DateField, SelectField, EmailField, FloatField, PasswordField
from wtforms import validators
from models import Usuario, Persona
from wtforms.validators import ValidationError, DataRequired, Email, Length, EqualTo, Regexp, Optional

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
        validators.Length(min=8, message="La contraseña debe tener al menos 8 caracteres."),
        validators.Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', message="La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial."),
        validators.Optional()
        ])
    
    confirmar_contrasena = PasswordField('Confirmar contraseña', [
        validators.DataRequired(message="La confirmación de contraseña es obligatoria."),
        validators.EqualTo('contrasena', message="Las contraseñas deben coincidir.")
    ])
    
    rol= SelectField('Rol', choices=[], coerce=str)
    
    def __init__(self, *args, **kwargs):
        super(RegistroUsuarioForm, self).__init__(*args, **kwargs)
      
        from models import Rol
        roles = Rol.query.all()
        self.rol.choices = [(rol.nombre, rol.nombre) for rol in roles]
    
    def validate_username(self, field):
        usuario = Usuario.query.filter_by(username=field.data).first()
        if usuario:
            raise ValidationError('Este nombre de usuario ya está registrado')
    
    def validate_correo(self, field):
        persona = Persona.query.filter_by(correo=field.data).first()
        if persona:
            raise ValidationError('Este correo ya está registrado')

    submit = SubmitField('Registrar usuario')
    
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

class RegistroProveedorForm(FlaskForm):
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
    
    submit = SubmitField('Registrar proveedor')
    

class EditarUsuarioForm(FlaskForm):
    nombre = StringField('Nombre', [    
                                    validators.Optional()
    ])
    apellido_p = StringField('Apellido Paterno', [
                                    validators.Optional()
    ])

    apellido_m = StringField('Apellido Materno', [
                                    validators.Optional()
    ])
    telefono = StringField('Teléfono', [
                                    validators.Optional(),
                                    validators.Regexp(r'^\d{10}$', message="El teléfono debe tener 10 dígitos.")
    ])
    correo = EmailField('Correo', [
                                    validators.Optional(),
                                    validators.Email(message="Ingrese un correo electrónico válido."),
                                    validators.Length(min=5, max=100, message="El correo debe tener entre 5 y 100 caracteres."),
                                    validators.Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message="El correo debe tener un formato válido.")
    ])
    direccion = StringField('Dirección', [
                                    validators.Optional(),  
                                    validators.Length(min=5, max=100, message="La dirección debe tener entre 5 y 100 caracteres.")
    ])
    username = StringField('Username', [
        validators.Optional(),
        validators.Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")
        ])
    
    contrasena = PasswordField('Contraseña', [
        validators.Optional(),
        validators.Length(min=8, message="La contraseña debe tener al menos 8 caracteres."),
        validators.Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', message="La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial.")  
        ])
    
    confirmar_contrasena = PasswordField('Confirmar contraseña', [
        validators.Optional(),
        validators.EqualTo('contrasena', message="Las contraseñas deben coincidir.")
    ])
    
    rol = SelectField('Rol', [
        validators.Optional()
        ], choices=[])
    
    submit= SubmitField('Actualizar usuario')
    
class EditarPerfilForm(FlaskForm):
    nombre = StringField('Nombre', [    
                                    validators.Optional()
    ])
    apellido_p = StringField('Apellido Paterno', [
                                    validators.Optional()
    ])

    apellido_m = StringField('Apellido Materno', [
                                    validators.Optional()
    ])
    telefono = StringField('Teléfono', [
                                    validators.Optional(),
                                    validators.Regexp(r'^\d{10}$', message="El teléfono debe tener 10 dígitos.")
    ])
    correo = EmailField('Correo', [
                                    validators.Optional(),
                                    validators.Email(message="Ingrese un correo electrónico válido."),
                                    validators.Length(min=5, max=100, message="El correo debe tener entre 5 y 100 caracteres."),
                                    validators.Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message="El correo debe tener un formato válido.")
    ])
    direccion = StringField('Dirección', [
                                    validators.Optional(),  
                                    validators.Length(min=5, max=100, message="La dirección debe tener entre 5 y 100 caracteres.")
    ])
    username = StringField('Username', [
        validators.Optional(),
        validators.Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")
        ])
    
    contrasena = PasswordField('Contraseña', [
        validators.Optional(),
        validators.Length(min=8, message="La contraseña debe tener al menos 8 caracteres."),
        validators.Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', message="La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial.")  
        ])
    
    confirmar_contrasena = PasswordField('Confirmar contraseña', [
        validators.Optional(),
        validators.EqualTo('contrasena', message="Las contraseñas deben coincidir.")
    ])
    
    submit= SubmitField('Actualizar perfil')
        
class EditarProveedorForm(FlaskForm):
    nombre = StringField('Nombre', [    
                                    validators.Optional()
    ])
    apellido_p = StringField('Apellido Paterno', [
                                    validators.Optional()
    ])

    apellido_m = StringField('Apellido Materno', [
                                    validators.Optional()
    ])
    telefono = StringField('Teléfono', [
                                    validators.Optional(),
                                    validators.Regexp(r'^\d{10}$', message="El teléfono debe tener 10 dígitos.")
    ])
    correo = EmailField('Correo', [
                                    validators.Optional(),
                                    validators.Email(message="Ingrese un correo electrónico válido."),
                                    validators.Length(min=5, max=100, message="El correo debe tener entre 5 y 100 caracteres."),
                                    validators.Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message="El correo debe tener un formato válido.")
    ])
    direccion = StringField('Dirección', [
                                    validators.Optional(),  
                                    validators.Length(min=5, max=100, message="La dirección debe tener entre 5 y 100 caracteres.")
    ])
    
    submit= SubmitField('Actualizar proveedor')


class CrearProductoForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.DataRequired(message="El nombre es obligatorio."),
        validators.Length(min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres.")
    ])
    
    descripcion = StringField('Descripción', [
        validators.Optional(),
        validators.Length(max=500, message="La descripción no debe exceder 500 caracteres.")
    ])
    
    precio = FloatField('Precio', [
        validators.DataRequired(message="El precio es obligatorio."),
        validators.NumberRange(min=0.01, message="El precio debe ser mayor a 0.")
    ])
    
    stock_actual = FloatField('Stock Actual', [
        validators.DataRequired(message="El stock actual es obligatorio."),
        validators.NumberRange(min=0, message="El stock no puede ser negativo.")
    ])
    
    stock_minimo = FloatField('Stock Mínimo', [
        validators.DataRequired(message="El stock mínimo es obligatorio."),
        validators.NumberRange(min=0, message="El stock mínimo no puede ser negativo.")
    ])
    
    id_categoria = SelectField('Categoría', [
        validators.DataRequired(message="Debe seleccionar una categoría.")
    ], coerce=int)
    
    imagen = StringField('URL Imagen (opcional)', [
        validators.Optional(),
        validators.URL(message="Ingrese una URL válida.")
    ])
    
    submit = SubmitField('Crear Producto')
    
    def __init__(self, *args, **kwargs):
        super(CrearProductoForm, self).__init__(*args, **kwargs)
        from models import Categoria
        categorias = Categoria.query.filter_by(estado=True).all()
        self.id_categoria.choices = [(cat.id_categoria, cat.nombre) for cat in categorias]


class EditarProductoForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.Optional(),
        validators.Length(min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres.")
    ])
    
    descripcion = StringField('Descripción', [
        validators.Optional(),
        validators.Length(max=500, message="La descripción no debe exceder 500 caracteres.")
    ])
    
    precio = FloatField('Precio', [
        validators.Optional(),
        validators.NumberRange(min=0.01, message="El precio debe ser mayor a 0.")
    ])
    
    stock_actual = FloatField('Stock Actual', [
        validators.Optional(),
        validators.NumberRange(min=0, message="El stock no puede ser negativo.")
    ])
    
    stock_minimo = FloatField('Stock Mínimo', [
        validators.Optional(),
        validators.NumberRange(min=0, message="El stock mínimo no puede ser negativo.")
    ])
    
    id_categoria = SelectField('Categoría', [
        validators.Optional()
    ], coerce=int)
    
    imagen = StringField('URL Imagen (opcional)', [
        validators.Optional(),
        validators.URL(message="Ingrese una URL válida.")
    ])
    
    submit = SubmitField('Actualizar Producto')
    
    def __init__(self, *args, **kwargs):
        super(EditarProductoForm, self).__init__(*args, **kwargs)
        from models import Categoria
        categorias = Categoria.query.filter_by(estado=True).all()
        self.id_categoria.choices = [(cat.id_categoria, cat.nombre) for cat in categorias]