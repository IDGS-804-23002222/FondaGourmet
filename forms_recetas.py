
class CrearRecetaForm(FlaskForm):
    """Formulario para crear una receta con ingredientes y rendimiento"""
    
    rendimiento = FloatField('Rendimiento (%)', [
        validators.DataRequired(message="El rendimiento es obligatorio."),
        validators.NumberRange(min=0, max=100, message="El rendimiento debe estar entre 0 y 100%.")
    ])

    porciones = IntegerField('Numero de porciones', [
        validators.DataRequired(message="El numero de porciones es obligatorio."),
        validators.NumberRange(min=1, message="El numero de porciones debe ser mayor a 0.")
    ])
    
    nota = TextAreaField('Notas (opcional)', [
        validators.Optional(),
        validators.Length(max=500, message="Las notas no pueden exceder 500 caracteres.")
    ])
    
    submit = SubmitField('Crear Receta')


class EditarRecetaForm(FlaskForm):
    """Formulario para editar una receta"""
    
    rendimiento = FloatField('Rendimiento (%)', [
        validators.DataRequired(message="El rendimiento es obligatorio."),
        validators.NumberRange(min=0, max=100, message="El rendimiento debe estar entre 0 y 100%.")
    ])

    porciones = IntegerField('Numero de porciones', [
        validators.DataRequired(message="El numero de porciones es obligatorio."),
        validators.NumberRange(min=1, message="El numero de porciones debe ser mayor a 0.")
    ])
    
    nota = TextAreaField('Notas (opcional)', [
        validators.Optional(),
        validators.Length(max=500, message="Las notas no pueden exceder 500 caracteres.")
    ])
    
    submit = SubmitField('Actualizar Receta')


class RecetaDetalleForm(FlaskForm):
    """Formulario para agregar ingredientes a una receta"""
    
    id_materia = SelectField('Ingrediente', coerce=int, validators=[
        validators.DataRequired(message="Debe seleccionar un ingrediente.")
    ])
    
    cantidad = FloatField('Cantidad', [
        validators.DataRequired(message="La cantidad es obligatoria."),
        validators.NumberRange(min=0.01, message="La cantidad debe ser mayor a 0.")
    ])
    
    submit = SubmitField('Agregar Ingrediente')
    
    def __init__(self, *args, **kwargs):
        super(RecetaDetalleForm, self).__init__(*args, **kwargs)
        from models import MateriaPrima
        ingredientes = MateriaPrima.query.filter_by(estado=True).all()
        self.id_materia.choices = [(ing.id_materia, f"{ing.nombre} ({ing.unidad_medida})") for ing in ingredientes]
