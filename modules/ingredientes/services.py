from models import db, MateriaPrima, Categoria, Proveedor
import logging

logger = logging.getLogger(__name__)


def _proveedor_nombre(proveedor):
    if not proveedor or not proveedor.persona:
        return 'N/A'
    return f"{proveedor.persona.nombre} {proveedor.persona.apellido_p or ''}".strip()


def _to_dict(materia):
    return {
        'id_materia': materia.id_materia,
        'nombre': materia.nombre,
        'unidad_medida': materia.unidad_medida,
        'stock_actual': materia.stock_actual,
        'stock_minimo': materia.stock_minimo,
        'porcentaje_merma': materia.porcentaje_merma,
        'factor_conversion': materia.factor_conversion,
        'estado': materia.estado,
        'categoria_nombre': materia.categoria.nombre if materia.categoria else 'N/A',
        'proveedor_nombre': _proveedor_nombre(materia.proveedor),
        'id_categoria': materia.id_categoria,
        'id_proveedor': materia.id_proveedor,
    }


def crear_ingrediente(form):
    try:
        existe = MateriaPrima.query.filter_by(nombre=form.nombre.data).first()
        if existe:
            return False, 'Ya existe un ingrediente con ese nombre.'

        nuevo = MateriaPrima(
            nombre=form.nombre.data,
            unidad_medida=form.unidad_medida.data,
            stock_actual=0,
            stock_minimo=form.stock_minimo.data,
            porcentaje_merma=form.porcentaje_merma.data,
            factor_conversion=form.factor_conversion.data,
            id_categoria=form.id_categoria.data,
            id_proveedor=form.id_proveedor.data,
            estado=True,
        )

        db.session.add(nuevo)
        db.session.commit()
        logger.info(f"Ingrediente creado: {nuevo.nombre}")
        return True, 'Ingrediente creado correctamente.'
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear ingrediente: {str(e)}")
        return False, str(e)


def obtener_ingredientes():
    try:
        materias = MateriaPrima.query.order_by(MateriaPrima.nombre.asc()).all()
        return [_to_dict(m) for m in materias], None
    except Exception as e:
        logger.error(f"Error al obtener ingredientes: {str(e)}")
        return None, str(e)


def filtrar_ingredientes(filtro):
    try:
        term = f"%{filtro}%"
        materias = MateriaPrima.query.join(Categoria).filter(
            (MateriaPrima.nombre.ilike(term)) |
            (Categoria.nombre.ilike(term))
        ).order_by(MateriaPrima.nombre.asc()).all()
        return [_to_dict(m) for m in materias], None
    except Exception as e:
        logger.error(f"Error al filtrar ingredientes: {str(e)}")
        return None, str(e)


def obtener_ingrediente(id_ingrediente):
    try:
        materia = MateriaPrima.query.get(id_ingrediente)
        if not materia:
            return None, 'Ingrediente no encontrado.'
        return _to_dict(materia), None
    except Exception as e:
        logger.error(f"Error al obtener ingrediente: {str(e)}")
        return None, str(e)


def actualizar_ingrediente(id_ingrediente, form):
    try:
        materia = MateriaPrima.query.get(id_ingrediente)
        if not materia:
            return False, 'Ingrediente no encontrado.'

        if form.nombre.data:
            existente = MateriaPrima.query.filter(
                MateriaPrima.nombre == form.nombre.data,
                MateriaPrima.id_materia != id_ingrediente
            ).first()
            if existente:
                return False, 'Ya existe otro ingrediente con ese nombre.'
            materia.nombre = form.nombre.data

        if form.unidad_medida.data:
            materia.unidad_medida = form.unidad_medida.data
        if form.stock_actual.data is not None:
            materia.stock_actual = form.stock_actual.data
        if form.stock_minimo.data is not None:
            materia.stock_minimo = form.stock_minimo.data
        if form.porcentaje_merma.data is not None:
            materia.porcentaje_merma = form.porcentaje_merma.data
        if form.factor_conversion.data is not None:
            materia.factor_conversion = form.factor_conversion.data
        if form.id_categoria.data:
            materia.id_categoria = form.id_categoria.data
        if form.id_proveedor.data:
            materia.id_proveedor = form.id_proveedor.data

        db.session.commit()
        return True, 'Ingrediente actualizado correctamente.'
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar ingrediente: {str(e)}")
        return False, str(e)


def desactivar_ingrediente(id_ingrediente):
    try:
        materia = MateriaPrima.query.get(id_ingrediente)
        if not materia:
            return False, 'Ingrediente no encontrado.'
        materia.estado = False
        db.session.commit()
        return True, 'Ingrediente desactivado correctamente.'
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al desactivar ingrediente: {str(e)}")
        return False, str(e)


def activar_ingrediente(id_ingrediente):
    try:
        materia = MateriaPrima.query.get(id_ingrediente)
        if not materia:
            return False, 'Ingrediente no encontrado.'
        materia.estado = True
        db.session.commit()
        return True, 'Ingrediente activado correctamente.'
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al activar ingrediente: {str(e)}")
        return False, str(e)
