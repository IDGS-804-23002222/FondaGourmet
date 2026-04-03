from models import db, Categoria
import logging

logger = logging.getLogger(__name__)


def _to_dict(categoria):
    return {
        'id_categoria': categoria.id_categoria,
        'nombre': categoria.nombre,
        'descripcion': categoria.descripcion,
        'estado': categoria.estado,
        'fecha_creacion': categoria.fecha_creacion,
    }


def crear_categoria(form):
    try:
        existe = Categoria.query.filter_by(nombre=form.nombre.data).first()
        if existe:
            return False, 'Ya existe una categoría con ese nombre.'

        categoria = Categoria(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data or None,
            estado=True,
        )
        db.session.add(categoria)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear categoría: {str(e)}")
        return False, str(e)


def obtener_categorias():
    try:
        categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
        return [_to_dict(c) for c in categorias], None
    except Exception as e:
        logger.error(f"Error al obtener categorías: {str(e)}")
        return None, str(e)


def obtener_categoria(id_categoria):
    try:
        categoria = Categoria.query.get(id_categoria)
        if not categoria:
            return None, 'Categoría no encontrada.'
        return _to_dict(categoria), None
    except Exception as e:
        logger.error(f"Error al obtener categoría: {str(e)}")
        return None, str(e)


def filtrar_categorias(filtro):
    try:
        term = f"%{filtro}%"
        categorias = Categoria.query.filter(
            (Categoria.nombre.ilike(term)) |
            (Categoria.descripcion.ilike(term))
        ).order_by(Categoria.nombre.asc()).all()
        return [_to_dict(c) for c in categorias], None
    except Exception as e:
        logger.error(f"Error al filtrar categorías: {str(e)}")
        return None, str(e)


def actualizar_categoria(id_categoria, form):
    try:
        categoria = Categoria.query.get(id_categoria)
        if not categoria:
            return False, 'Categoría no encontrada.'

        if form.nombre.data:
            existe = Categoria.query.filter(
                Categoria.nombre == form.nombre.data,
                Categoria.id_categoria != id_categoria
            ).first()
            if existe:
                return False, 'Ya existe otra categoría con ese nombre.'
            categoria.nombre = form.nombre.data

        categoria.descripcion = form.descripcion.data or None
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar categoría: {str(e)}")
        return False, str(e)


def desactivar_categoria(id_categoria):
    try:
        categoria = Categoria.query.get(id_categoria)
        if not categoria:
            return False, 'Categoría no encontrada.'
        categoria.estado = False
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al desactivar categoría: {str(e)}")
        return False, str(e)


def activar_categoria(id_categoria):
    try:
        categoria = Categoria.query.get(id_categoria)
        if not categoria:
            return False, 'Categoría no encontrada.'
        categoria.estado = True
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al activar categoría: {str(e)}")
        return False, str(e)
