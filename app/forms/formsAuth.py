from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, RadioField, BooleanField, DateField, SelectField
from wtforms import validators

class LoginForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(message="El nombre de usuario es obligatorio."),
        validators.Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")
        ])
    
    correo = StringField('Correo', [
        validators.DataRequired(message="El correo es obligatorio."),
        validators.Email(message="El correo no es válido.")
        ])
    
    contrasena = StringField('Contraseña', [
        validators.DataRequired(message="La contraseña es obligatoria."),
        validators.Length(min=6, message="La contraseña debe tener al menos 6 caracteres.")
        ])

    submit = SubmitField('Iniciar Sesión')