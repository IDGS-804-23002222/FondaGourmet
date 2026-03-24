from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, RadioField, BooleanField, DateField, SelectField
from wtforms import validators

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre',[
        validators.DataRequired(message='El nombre es obligatorio'),
        validators.length(min=2,max=100)
    ])