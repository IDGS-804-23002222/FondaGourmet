from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, IntegerField, SubmitField, RadioField, BooleanField, DateField, SelectField, EmailField, FloatField, PasswordField, TextAreaField, HiddenField
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
        validators.Length(min=5, max=100, message="El correo debe tener entre 5 y 100 caracteres.")
        ])
    
    direccion = StringField('Dirección', [
        validators.Length(min=5, max=100, message="La dirección debe tener entre 5 y 100 caracteres.")
        ])

    id_categoria_proveedor = SelectField('Categoría de proveedor', coerce=int, validators=[
        validators.Optional()
    ])

    usar_categoria_nueva = BooleanField('Crear nueva categoría de proveedor')
    nombre_nueva_categoria = StringField('Nombre nueva categoría', [
        validators.Optional(),
        validators.Length(min=2, max=100, message="La nueva categoría debe tener entre 2 y 100 caracteres.")
    ])
    
    submit = SubmitField('Registrar proveedor')

    def __init__(self, *args, **kwargs):
        super(RegistroProveedorForm, self).__init__(*args, **kwargs)
        from models import CategoriaProveedor
        categorias = CategoriaProveedor.query.filter_by(estado=True).order_by(CategoriaProveedor.nombre.asc()).all()
        self.id_categoria_proveedor.choices = [(c.id_categoria_proveedor, c.nombre) for c in categorias]

    def validate_nombre_nueva_categoria(self, field):
        if self.usar_categoria_nueva.data and not (field.data or '').strip():
            raise ValidationError('Debes capturar el nombre de la nueva categoría o desmarcar el check.')

    def validate(self, extra_validators=None):
        if not super(RegistroProveedorForm, self).validate(extra_validators=extra_validators):
            return False

        usar_nueva = bool(self.usar_categoria_nueva.data)
        nombre_nueva = (self.nombre_nueva_categoria.data or '').strip()

        if usar_nueva and nombre_nueva:
            return True

        if not usar_nueva and self.id_categoria_proveedor.data:
            return True

        self.id_categoria_proveedor.errors.append('La categoría de proveedor es obligatoria o marca el check para crear una nueva.')
        return False
    

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

    id_categoria_proveedor = SelectField('Categoría de proveedor', coerce=int, validators=[
        validators.Optional()
    ])

    usar_categoria_nueva = BooleanField('Crear nueva categoría de proveedor')
    nombre_nueva_categoria = StringField('Nombre nueva categoría', [
        validators.Optional(),
        validators.Length(min=2, max=100, message="La nueva categoría debe tener entre 2 y 100 caracteres.")
    ])
    
    submit= SubmitField('Actualizar proveedor')

    def __init__(self, *args, **kwargs):
        super(EditarProveedorForm, self).__init__(*args, **kwargs)
        from models import CategoriaProveedor
        categorias = CategoriaProveedor.query.filter_by(estado=True).order_by(CategoriaProveedor.nombre.asc()).all()
        self.id_categoria_proveedor.choices = [(c.id_categoria_proveedor, c.nombre) for c in categorias]

    def validate_nombre_nueva_categoria(self, field):
        if self.usar_categoria_nueva.data and not (field.data or '').strip():
            raise ValidationError('Debes capturar el nombre de la nueva categoría o desmarcar el check.')

    def validate(self, extra_validators=None):
        if not super(EditarProveedorForm, self).validate(extra_validators=extra_validators):
            return False

        usar_nueva = bool(self.usar_categoria_nueva.data)
        nombre_nueva = (self.nombre_nueva_categoria.data or '').strip()

        if usar_nueva and nombre_nueva:
            return True

        if not usar_nueva and self.id_categoria_proveedor.data:
            return True

        self.id_categoria_proveedor.errors.append('La categoría de proveedor es obligatoria o marca el check para crear una nueva.')
        return False

class RegistrarCategoriaForm(FlaskForm):
    nombre = StringField('Nombre de categoría', [
        validators.DataRequired(message="El nombre de la categoría es obligatorio."),
        validators.Length(min=2, max=50, message="El nombre de la categoría debe tener entre 2 y 50 caracteres.")
    ])
    
    descripcion = StringField('Descripción', [
        validators.Optional(),
        validators.Length(max=200, message="La descripción no puede exceder los 200 caracteres.")
    ])
    
    tipo_categoria = SelectField('Tipo de categoría', [
        validators.DataRequired(message="El tipo de categoría es obligatorio.")
    ], choices=[
        ('platillo', 'Platillo/Producto'),
        ('ingrediente', 'Ingrediente')
    ])
    
    submit = SubmitField('Registrar categoría')
    
class EditarCategoriaForm(FlaskForm):
    nombre = StringField('Nombre de categoría', [
        validators.Optional(),
        validators.Length(min=2, max=50, message="El nombre de la categoría debe tener entre 2 y 50 caracteres.")
    ])
    
    descripcion = StringField('Descripción', [
        validators.Optional(),
        validators.Length(max=200, message="La descripción no puede exceder los 200 caracteres.")
    ])
    
    tipo_categoria = SelectField('Tipo de categoría', [
        validators.Optional()
    ], choices=[
        ('platillo', 'Platillo/Producto'),
        ('ingrediente', 'Ingrediente')
    ])
    
    submit = SubmitField('Actualizar categoría')
    
class RegistrarIngredienteForm(FlaskForm):
    nombre = StringField('Nombre del ingrediente', [
        validators.DataRequired(message="El nombre del ingrediente es obligatorio."),
        validators.Length(min=2, max=50, message="El nombre del ingrediente debe tener entre 2 y 50 caracteres.")
    ])
    
    unidad_medida = SelectField('Unidad de medida', [
        validators.DataRequired(message="La unidad de medida es obligatoria."),
        validators.Length(min=1, max=20, message="La unidad de medida debe tener entre 1 y 20 caracteres.")
    ], choices=[
        ('kg', 'Kilogramos'), 
        ('g', 'Gramos'), 
        ('l', 'Litros'), 
        ('ml', 'Mililitros'), 
        ('pz', 'Piezas')
    ])
    
    stock_minimo = FloatField('Stock mínimo', [
        validators.DataRequired(message="El stock mínimo es obligatorio."),
        validators.NumberRange(min=0, message="El stock mínimo no puede ser negativo.")
    ])

    precio = FloatField('Precio', [
        validators.DataRequired(message="El precio es obligatorio."),
        validators.NumberRange(min=0, message="El precio no puede ser negativo.")
    ])
    
    porcentaje_merma = FloatField('Porcentaje de mermas', [
        validators.DataRequired(message="El porcentaje de mermas es obligatorio."),
        validators.NumberRange(min=0, max=100, message="El porcentaje de mermas debe estar entre 0 y 100.")
    ])
    
    factor_conversion = FloatField('Factor de conversión', [
        validators.DataRequired(message="El factor de conversión es obligatorio."),
        validators.NumberRange(min=0.0001, message="El factor de conversión no puede ser cero.")
    ])
        
    id_categoria_ingrediente = SelectField('Categoría ingrediente', coerce=int, validators=[
        validators.DataRequired(message="La categoría es obligatoria.")
    ])
    
    id_proveedor = SelectField('Proveedor', coerce=int, validators=[
        validators.DataRequired(message="El proveedor es obligatorio.")
    ])
    
    submit = SubmitField('Registrar ingrediente')
    
    def __init__(self, *args, **kwargs):
        super(RegistrarIngredienteForm, self).__init__(*args, **kwargs)
        from models import CategoriaIngrediente, Proveedor
        categorias = CategoriaIngrediente.query.filter_by(estado=True).order_by(CategoriaIngrediente.nombre.asc()).all()
        proveedores = Proveedor.query.all()
        self.id_categoria_ingrediente.choices = [(cat.id_categoria_ingrediente, cat.nombre) for cat in categorias]
        self.id_proveedor.choices = [(p.id_proveedor, p.persona.nombre) for p in proveedores]
    
class EditarIngredienteForm(FlaskForm):
    nombre = StringField('Nombre del ingrediente', [
        validators.Optional(),
        validators.Length(min=2, max=50)
    ])
    
    unidad_medida = SelectField('Unidad de medida', [
        validators.Optional(),
        validators.Length(min=1, max=20)
    ], choices=[
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('pz', 'Piezas')
    ])
    
    stock_actual = FloatField('Stock actual', [
        validators.Optional(),
        validators.NumberRange(min=0, message="El stock actual no puede ser negativo.")
    ])
    
    stock_minimo = FloatField('Stock mínimo', [
        validators.Optional(),
        validators.NumberRange(min=0, message="El stock mínimo no puede ser negativo."  )
    ])

    precio = FloatField('Precio', [
        validators.Optional(),
        validators.NumberRange(min=0, message="El precio no puede ser negativo.")
    ])
    
    porcentaje_merma = FloatField('Porcentaje de mermas', [
        validators.Optional(),
        validators.NumberRange(min=0, max=100, message="El porcentaje de mermas debe estar entre 0 y 100.")
    ])
    
    factor_conversion = FloatField('Factor de conversión', [
        validators.Optional(),
        validators.NumberRange(min=0.0001, message="El factor de conversión no puede ser cero.")  # 🔥 nunca 0
    ])

    id_categoria_ingrediente = SelectField('Categoría ingrediente', coerce=int, validators=[validators.Optional()])
    id_proveedor = SelectField('Proveedor', coerce=int, validators=[validators.Optional()])
    
    submit = SubmitField('Actualizar ingrediente')
    
    def __init__(self, *args, **kwargs):
        super(EditarIngredienteForm, self).__init__(*args, **kwargs)
        from models import CategoriaIngrediente, Proveedor
        categorias = CategoriaIngrediente.query.filter_by(estado=True).order_by(CategoriaIngrediente.nombre.asc()).all()
        proveedores = Proveedor.query.all()
        self.id_categoria_ingrediente.choices = [(cat.id_categoria_ingrediente, cat.nombre) for cat in categorias]
        self.id_proveedor.choices = [(p.id_proveedor, p.persona.nombre) for p in proveedores]


class RegistrarCompraIngredienteForm(FlaskForm):
    id_materia = SelectField('Ingrediente', coerce=int, validators=[
        validators.DataRequired(message="Debe seleccionar un ingrediente.")
    ])
    
    cantidad = FloatField('Cantidad comprada', [
        validators.DataRequired(message="La cantidad comprada es obligatoria."),
        validators.NumberRange(min=0.01, message="La cantidad comprada debe ser un valor positivo.")
    ])
    
    precio_u = FloatField('Precio unitario', [
        validators.DataRequired(message="El precio unitario es obligatorio."),
        validators.NumberRange(min=0, message="El precio unitario no puede ser negativo.")
    ])
    
    submit = SubmitField('Registrar compra')



class PersonaForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.DataRequired(),
        validators.Length(min=2, max=100)
    ])
    
    apellido_p = StringField('Apellido paterno', [
        validators.DataRequired(),
        validators.Length(min=2, max=50)
    ])
    
    apellido_m = StringField('Apellido materno', [
        validators.Optional(),
        validators.Length(max=50)
    ])
    
    telefono = StringField('Teléfono', [
        validators.DataRequired(),
        validators.Regexp(r'^\d{10}$', message="Debe tener 10 dígitos")
    ])
    
    correo = StringField('Correo', [
        validators.DataRequired(),
        validators.Email()
    ])
    
    direccion = StringField('Dirección', [
        validators.Optional(),
        validators.Length(max=200)
    ])

class UsuarioForm(FlaskForm):
    username = StringField('Usuario', [
        validators.DataRequired(),
        validators.Length(min=4, max=100)
    ])
    
    password = PasswordField('Contraseña', [
        validators.DataRequired(),
        validators.Length(min=6)
    ])
    
    id_rol = SelectField('Rol', coerce=int)


class ClienteForm(PersonaForm, UsuarioForm):
    submit = SubmitField('Registrar Cliente')


class EmpleadoForm(PersonaForm, UsuarioForm):
    submit = SubmitField('Registrar Empleado')


class ProveedorForm(PersonaForm):
    submit = SubmitField('Registrar Proveedor')

class MateriaPrimaForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.DataRequired(),
        validators.Length(max=100)
    ])

    unidad_medida = SelectField('Unidad', choices=[
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('pz', 'Piezas')
    ])

    stock_actual = FloatField('Stock actual', [
        validators.Optional(),
        validators.NumberRange(min=0)
    ])

    stock_minimo = FloatField('Stock mínimo', [
        validators.DataRequired(),
        validators.NumberRange(min=0)
    ])

    porcentaje_merma = FloatField('Merma (%)', [
        validators.DataRequired(),
        validators.NumberRange(min=0, max=100)
    ])

    factor_conversion = FloatField('Factor conversión', [
        validators.DataRequired(),
        validators.NumberRange(min=0.0001)
    ])

    id_categoria_ingrediente = SelectField('Categoría ingrediente', coerce=int)
    id_proveedor = SelectField('Proveedor', coerce=int)

    submit = SubmitField('Guardar')

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', [validators.DataRequired()])
    descripcion = TextAreaField('Descripción')
    
    precio = FloatField('Precio', [
        validators.DataRequired(),
        validators.NumberRange(min=0)
    ])
    
    stock_minimo = FloatField('Stock mínimo', [
        validators.DataRequired(),
        validators.NumberRange(min=0)
    ])
    
    imagen = StringField('URL Imagen')
    
    id_categoria_platillo = SelectField('Categoría platillo', coerce=int)

    submit = SubmitField('Guardar Producto')

class RecetaForm(FlaskForm):
    id_producto = SelectField('Producto', coerce=int)
    submit = SubmitField('Crear Receta')

class RecetaDetalleForm(FlaskForm):
    id_materia = SelectField('Materia Prima', coerce=int)
    
    cantidad = FloatField('Cantidad', [
        validators.DataRequired(),
        validators.NumberRange(min=0.01)
    ])

    submit = SubmitField('Agregar Ingrediente')

class RecetaDetalleForm(FlaskForm):
    id_materia = SelectField('Materia Prima', coerce=int)
    
    cantidad = FloatField('Cantidad', [
        validators.DataRequired(),
        validators.NumberRange(min=0.01)
    ])

    submit = SubmitField('Agregar Ingrediente')

class CompraForm(FlaskForm):
    id_proveedor = SelectField('Proveedor', coerce=int)
    metodo_pago = SelectField('Método de pago', choices=[
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia')
    ])
    
    submit = SubmitField('Registrar Compra')

class DetalleCompraForm(FlaskForm):
    id_materia = SelectField('Materia Prima', coerce=int)
    
    cantidad = FloatField('Cantidad', [
        validators.DataRequired(),
        validators.NumberRange(min=0.01)
    ])
    
    precio_u = FloatField('Precio unitario', [
        validators.DataRequired(),
        validators.NumberRange(min=0)
    ])

    submit = SubmitField('Agregar')

class VentaForm(FlaskForm):
    metodo_pago = SelectField('Método de pago', choices=[
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia')
    ])
    
    submit = SubmitField('Registrar Venta')

class DetalleVentaForm(FlaskForm):
    id_producto = SelectField('Producto', coerce=int)
    
    cantidad = IntegerField('Cantidad', [
        validators.DataRequired(),
        validators.NumberRange(min=1)
    ])

    submit = SubmitField('Agregar')

class CategoriaForm(FlaskForm):
    nombre = StringField('Nombre', [validators.DataRequired()])
    descripcion = TextAreaField('Descripción')
    submit = SubmitField('Guardar Categoría')


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
    
    id_categoria_platillo = SelectField('Categoría platillo', [
        validators.DataRequired(message="Debe seleccionar una categoría.")
    ], coerce=int)

    ingredientes_json = HiddenField('Ingredientes receta')
    
    imagen = FileField('Imagen', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo se permiten imágenes JPG, JPEG, PNG o WEBP.')
    ])
    
    submit = SubmitField('Crear Producto')
    
    def __init__(self, *args, **kwargs):
        super(CrearProductoForm, self).__init__(*args, **kwargs)
        from models import CategoriaPlatillo
        categorias = CategoriaPlatillo.query.filter_by(estado=True).order_by(CategoriaPlatillo.nombre.asc()).all()
        self.id_categoria_platillo.choices = [(cat.id_categoria_platillo, cat.nombre) for cat in categorias]


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
    
    id_categoria_platillo = SelectField('Categoría platillo', [
        validators.Optional()
    ], coerce=int)
    
    imagen = FileField('Reemplazar imagen', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo se permiten imágenes JPG, JPEG, PNG o WEBP.')
    ])
    
    submit = SubmitField('Actualizar Producto')
    
    def __init__(self, *args, **kwargs):
        super(EditarProductoForm, self).__init__(*args, **kwargs)
        from models import CategoriaPlatillo
        categorias = CategoriaPlatillo.query.filter_by(estado=True).order_by(CategoriaPlatillo.nombre.asc()).all()
        self.id_categoria_platillo.choices = [(cat.id_categoria_platillo, cat.nombre) for cat in categorias]