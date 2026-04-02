from sqlalchemy import text
from models import db
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def aplicar_merma(cantidad, merma):
    return cantidad * (1 - (merma / 100))


def convertir_unidad(cantidad, factor):
    return cantidad * factor

def crear_ingrediente(form):
    try:
        
        logger.info(f"Creando ingrediente: {form.nombre.data}")
        
        db.session.execute(text("""
            CALL sp_crearMateriaPrima(
                :n,:u,:s,:m,:f,:c,:p
            )
        """), {
            "n": form.nombre.data,
            "u": form.unidad.data,
            "s": form.stock.data,
            "m": form.merma.data,
            "f": form.factor.data,
            "c": form.costo.data,
            "p": form.precio.data
        })

        db.session.commit()
        logger.info(f"Ingrediente creado: {form.nombre.data}")
        return True, "Ingrediente creado exitosamente"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear ingrediente: {str(e)}")
        return False, str(e)

def obtener_ingredientes():
    try:
        logger.info("Obteniendo ingredientes")
        return db.session.execute(text("SELECT * FROM v_materias_primas")).fetchall(), None
    except Exception as e:
        logger.error(f"Error al obtener ingredientes: {str(e)}")
        return None, str(e)

def filtrar_ingredientes(f):
    try:
        return db.session.execute(text("""CALL sp_filtrarMaterias(:f)"""), {"f": f}).fetchall(), None
    except Exception as e:
        logger.error(f"Error al filtrar ingredientes: {str(e)}")
        return None, str(e)
    
def desactivar_ingrediente(id_ingrediente):
    try:
        db.session.execute(
            text("CALL sp_eliminarMateriaPrima(:id_ingrediente)"), 
            {"id_ingrediente": id_ingrediente}
        )
        db.session.commit()
        logger.info(f"Ingrediente {id_ingrediente} desactivado")
        return True, "Ingrediente desactivado exitosamente"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al desactivar ingrediente: {str(e)}")
        return False, str(e)

def activar_ingrediente(id_ingrediente):
    try:
        db.session.execute(
            text("CALL sp_activarMateriaPrima(:id_ingrediente)"), 
            {"id_ingrediente": id_ingrediente}
        )
        db.session.commit()
        logger.info(f"Ingrediente {id_ingrediente} activado")
        return True, "Ingrediente activado exitosamente"
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al activar ingrediente: {str(e)}")
        return False, str(e)

def actualizar_ingrediente(id_ingrediente, form):
    try:
        if not id_ingrediente:
            return False, "ID inválido"

        if not form.validate():
            return False, "Formulario inválido"

        logger.info(f"Actualizando ingrediente ID: {id_ingrediente}")

        db.session.execute(text("""
            CALL sp_actualizarMateriaPrima(
                :id, :nom, :uni, :stock, :merma, :factor, :cat, :prov
            )
        """), {
            "id": id_ingrediente,
            "nom": form.nombre.data or None,
            "uni": form.unidad_medida.data or None,
            "stock": form.stock_minimo.data,
            "merma": form.porcentaje_merma.data,
            "factor": form.factor_conversion.data,
            "cat": form.id_categoria.data,
            "prov": form.id_proveedor.data
        })

        db.session.commit()

        logger.info("Ingrediente actualizado correctamente")
        return True, "Ingrediente actualizado"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar ingrediente: {str(e)}")
        return False, str(e)

def descontar_stock(materia, cantidad):
    # conversión
    cantidad_convertida = cantidad * materia.factor_conversion

    # merma
    merma = cantidad_convertida * (materia.porcentaje_merma / 100)

    consumo_total = cantidad_convertida + merma

    if materia.stock_actual < consumo_total:
        raise Exception(f"Stock insuficiente de {materia.nombre}")

    materia.stock_actual -= consumo_total
