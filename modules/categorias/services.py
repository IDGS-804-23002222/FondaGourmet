from sqlalchemy import text
from models import db
from flask import current_app
import logging

logger = logging.getLogger(__name__)
def crear_categoria(form):
    try:
        
        logger.info(f"Creando categoría: {form.nombre.data}")
        
        db.session.execute(text("""
            CALL sp_crearCategoria(
                :n, :d
            )
        """), {
            "n": form.nombre.data,
            "d": form.descripcion.data
        })

        db.session.commit()
        logger.info(f"Categoría creada: {form.nombre.data}")
        return True, "Categoría creada exitosamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear categoría: {str(e)}")
        return False, str(e)
          

def obtener_categorias():
    try:
        logger.info("Obteniendo categorías")
        resultados = db.session.execute(text("SELECT * FROM v_categorias")).fetchall()
        return resultados, None
    except Exception as e:
        logger.error(f"Error al obtener categorías: {str(e)}")
        return None, str(e)

def filtrar_categorias(f):
    try:
        logger.info(f"Filtrando categorías con: {f}")
        categoria = db.session.execute(text("CALL sp_filtrarCategorias(:f)"), {"f": f}).fetchall()
        return categoria, None
    except Exception as e:
        logger.error(f"Error al filtrar categorías: {str(e)}")
        return None, str(e)