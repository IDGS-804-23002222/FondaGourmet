from datetime import datetime, timedelta

from flask import current_app, has_app_context
from sqlalchemy import text

from models import db, Producto, InventarioTerminado


def _tabla_mermas_disponible():
    row = db.session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
              AND table_name = 'mermas'
            """
        )
    ).scalar()
    return bool(row)


def _resolver_usuario_sistema_id():
    # Prefer an admin/cashier as accountable user for automatic waste entries.
    row = db.session.execute(
        text(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE estado = 1 AND id_rol IN (1, 3)
            ORDER BY id_usuario ASC
            LIMIT 1
            """
        )
    ).mappings().first()
    if row:
        return int(row['id_usuario'])

    fallback = db.session.execute(
        text(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE estado = 1
            ORDER BY id_usuario ASC
            LIMIT 1
            """
        )
    ).mappings().first()
    return int(fallback['id_usuario']) if fallback else None


def _costo_unitario_merma_producto(producto):
    # Keep cost model aligned with manual waste registration.
    porciones_base = 1
    if producto and producto.recetas:
        porciones_base = int((producto.recetas[0].rendimiento_porciones or 1) if producto.recetas[0] else 1)
    return round(float(producto.precio or 0) / max(1, porciones_base), 2)


def _registrar_bitacora_merma_mongo(payload):
    if not has_app_context():
        return

    mongo_db = getattr(current_app, 'mongo', None)
    if mongo_db is None:
        return

    bitacora_doc = {
        'fecha': datetime.utcnow(),
        'modulo': 'seguridad.mermas',
        'metodo': 'AUTO',
        'endpoint': 'product_freshness.aplicar_merma_automatica_productos',
        'ruta': 'auto/mermas/frescura',
        'status_code': 201,
        'usuario': {
            'id_usuario': payload.get('id_usuario_registro'),
            'username': 'sistema',
            'rol': 'sistema',
        },
        'accion': 'Registro de Merma Automatica',
        'descripcion': f"Merma automatica por caducidad producto={payload.get('id_producto')} costo={payload.get('costo_perdida')}",
        'ip': '127.0.0.1',
        'payload_merma': payload,
    }
    mongo_db.bitacora_acciones.insert_one(bitacora_doc)


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
    tabla_mermas_ok = _tabla_mermas_disponible()
    usuario_sistema_id = _resolver_usuario_sistema_id() if tabla_mermas_ok else None

    for producto in productos:
        limite_merma = producto.fecha_produccion + timedelta(days=3)
        if ahora > limite_merma:
            stock_vencido = float(producto.stock_actual or 0)
            costo_unitario = _costo_unitario_merma_producto(producto)
            costo_perdida = round(stock_vencido * costo_unitario, 2)

            inventario = InventarioTerminado.query.filter_by(id_producto=producto.id_producto).first()
            if inventario:
                inventario.cantidad_disponible = 0
                inventario.fecha_actualizacion = ahora
            producto.fecha_merma = ahora
            actualizados += 1

            if tabla_mermas_ok and usuario_sistema_id and stock_vencido > 0:
                observaciones = (
                    f"Merma automatica por caducidad (>3 dias). "
                    f"fecha_produccion={producto.fecha_produccion.strftime('%Y-%m-%d %H:%M:%S') if producto.fecha_produccion else 'N/A'}"
                )

                db.session.execute(
                    text(
                        """
                        INSERT INTO mermas (
                            tipo_origen, id_materia, id_inventario, id_producto, cantidad, costo_unitario,
                            costo_perdida, motivo, observaciones, autorizada,
                            id_usuario_registro, id_usuario_autorizacion, fecha
                        ) VALUES (
                            'InventarioTerminado', NULL, NULL, :id_producto, :cantidad, :costo_unitario,
                            :costo_perdida, 'Caducado', :observaciones, 1,
                            :id_usuario_registro, :id_usuario_autorizacion, :fecha
                        )
                        """
                    ),
                    {
                        'id_producto': int(producto.id_producto),
                        'cantidad': stock_vencido,
                        'costo_unitario': costo_unitario,
                        'costo_perdida': costo_perdida,
                        'observaciones': observaciones,
                        'id_usuario_registro': usuario_sistema_id,
                        'id_usuario_autorizacion': usuario_sistema_id,
                        'fecha': ahora,
                    },
                )

                _registrar_bitacora_merma_mongo(
                    {
                        'tipo_origen': 'InventarioTerminado',
                        'id_inventario': None,
                        'id_producto': int(producto.id_producto),
                        'cantidad': stock_vencido,
                        'costo_unitario': costo_unitario,
                        'costo_perdida': costo_perdida,
                        'motivo': 'Caducado',
                        'observaciones': observaciones,
                        'id_usuario_registro': usuario_sistema_id,
                        'id_usuario_autorizacion': usuario_sistema_id,
                    }
                )

    if actualizados:
        db.session.commit()

    return actualizados
