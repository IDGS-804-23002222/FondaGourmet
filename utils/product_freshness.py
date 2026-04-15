from datetime import datetime, timedelta

from models import db, Producto


def aplicar_merma_automatica_productos():
    """Convierte a merma el stock de productos con mas de 3 dias desde produccion.

    Regla:
    - Si fecha_produccion + 3 dias < ahora y hay stock, el stock pasa a 0
      y se marca fecha_merma.
    """
    ahora = datetime.utcnow()
    productos = (
        Producto.query
        .filter(Producto.stock_actual > 0, Producto.fecha_produccion.isnot(None))
        .all()
    )

    actualizados = 0
    for producto in productos:
        limite_merma = producto.fecha_produccion + timedelta(days=3)
        if ahora > limite_merma:
            producto.stock_actual = 0
            producto.fecha_merma = ahora
            actualizados += 1

    if actualizados:
        db.session.commit()

    return actualizados
