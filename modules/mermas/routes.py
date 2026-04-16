import os
from datetime import datetime, timedelta

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from constants import MotivoMerma

from models import InventarioTerminado, MateriaPrima, Producto, Merma, db
from utils.security import role_required
from . import mermas

MONTO_MAX_SIN_AUTORIZACION_ADMIN = 500.0
MOTIVOS_VALIDOS = {motivo.value for motivo in MotivoMerma}


def _normalizar_motivo_merma(motivo_raw):
    motivo = (motivo_raw or '').strip()
    mapa = {
        'Caducado': MotivoMerma.CADUCIDAD.value,
        'Caducidad': MotivoMerma.CADUCIDAD.value,
        'Danado': MotivoMerma.DANO.value,
        'Dañado': MotivoMerma.DANO.value,
        'Daño': MotivoMerma.DANO.value,
        'Error de Produccion': MotivoMerma.ERROR_PRODUCCION.value,
        'Error de Producción': MotivoMerma.ERROR_PRODUCCION.value,
        'Robo': MotivoMerma.ROBO.value,
        'Otro': MotivoMerma.OTRO.value,
    }
    return mapa.get(motivo)


def _motivo_a_texto(motivo):
    if hasattr(motivo, 'value'):
        return str(motivo.value)
    return str(motivo or '').strip()


def _merma_payload_key(tipo_origen, articulo_id, cantidad, costo_perdida, motivo):
    try:
        articulo = int(articulo_id) if articulo_id is not None else None
    except (TypeError, ValueError):
        articulo = None

    try:
        cant = round(float(cantidad or 0), 4)
    except (TypeError, ValueError):
        cant = 0.0

    try:
        costo = round(float(costo_perdida or 0), 2)
    except (TypeError, ValueError):
        costo = 0.0

    return (
        (tipo_origen or '').strip(),
        articulo,
        cant,
        costo,
        _motivo_a_texto(motivo),
    )


def _merma_key_from_payload(payload):
    tipo_origen = (payload.get('tipo_origen') or '').strip()
    if tipo_origen == 'MateriaPrima':
        articulo_id = payload.get('id_materia')
    elif tipo_origen == 'InventarioTerminado':
        articulo_id = payload.get('id_inventario')
    else:
        articulo_id = None

    return _merma_payload_key(
        tipo_origen=tipo_origen,
        articulo_id=articulo_id,
        cantidad=payload.get('cantidad'),
        costo_perdida=payload.get('costo_perdida'),
        motivo=payload.get('motivo'),
    )


def _registrar_log_merma_mongo(payload):
    try:
        mongo_db = getattr(current_app, 'mongo', None)
        if mongo_db is None:
            return

        bitacora_doc = {
            'fecha': datetime.utcnow(),
            'modulo': 'seguridad.mermas',
            'metodo': 'POST',
            'endpoint': 'mermas.registrar',
            'ruta': '/mermas/',
            'status_code': 201,
            'usuario': {
                'id_usuario': payload.get('id_usuario_registro'),
                'username': getattr(current_user, 'username', None),
                'rol': getattr(current_user, 'id_rol', None),
            },
            'accion': 'Registro de Merma',
            'descripcion': f"Merma {payload.get('tipo_origen')} motivo={payload.get('motivo')} costo={payload.get('costo_perdida')}",
            'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
            'payload_merma': payload,
        }

        mongo_db.bitacora_acciones.insert_one(bitacora_doc)
    except Exception as exc:
        current_app.logger.warning(f'No se pudo registrar merma en Mongo: {exc}')


def _obtener_mongo_db():
    return getattr(current_app, 'mongo', None)


@mermas.route('/', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def registrar():
    if request.method == 'POST':
        tipo_origen = (request.form.get('tipo_origen') or '').strip()
        motivo = _normalizar_motivo_merma(request.form.get('motivo'))
        observaciones = (request.form.get('observaciones') or '').strip() or None

        try:
            cantidad = float((request.form.get('cantidad') or '0').strip())
        except Exception:
            flash('Cantidad invalida', 'danger')
            return redirect(url_for('mermas.registrar'))

        if cantidad <= 0:
            flash('La cantidad debe ser mayor a cero', 'danger')
            return redirect(url_for('mermas.registrar'))

        if not motivo:
            flash('Motivo de merma invalido', 'danger')
            return redirect(url_for('mermas.registrar'))

        try:
            with db.session.begin_nested():
                if tipo_origen == 'MateriaPrima':
                    id_materia = int(request.form.get('id_materia') or 0)
                    materia = MateriaPrima.query.get(id_materia)
                    if not materia:
                        raise ValueError('Ingrediente no encontrado')
                    if float(materia.stock_actual or 0) < cantidad:
                        raise ValueError('Stock insuficiente de ingrediente para registrar merma')

                    costo_unitario = float(materia.precio or 0)
                    costo_perdida = round(cantidad * costo_unitario, 2)

                    autorizada = 1
                    id_usuario_autorizacion = None
                    if costo_perdida > MONTO_MAX_SIN_AUTORIZACION_ADMIN:
                        if int(getattr(current_user, 'id_rol', 0) or 0) != 1:
                            raise ValueError(
                                f'Merma mayor a ${MONTO_MAX_SIN_AUTORIZACION_ADMIN:.2f} requiere autorizacion Admin'
                            )
                        id_usuario_autorizacion = int(current_user.id_usuario)

                    materia.stock_actual = float(materia.stock_actual or 0) - cantidad

                    db.session.add(Merma(
                        tipo_articulo='MateriaPrima',
                        articulo_id=id_materia,
                        cantidad=float(cantidad),
                        motivo=motivo,
                        costo_perdida=round(costo_perdida, 2),
                        fecha_registro=datetime.utcnow(),
                        usuario_id=int(current_user.id_usuario),
                    ))

                    payload_log = {
                        'tipo_origen': 'MateriaPrima',
                        'id_materia': id_materia,
                        'cantidad': cantidad,
                        'costo_unitario': costo_unitario,
                        'costo_perdida': costo_perdida,
                        'motivo': motivo,
                        'observaciones': observaciones,
                        'id_usuario_registro': int(current_user.id_usuario),
                        'id_usuario_autorizacion': id_usuario_autorizacion,
                    }

                elif tipo_origen == 'InventarioTerminado':
                    id_inventario = int(request.form.get('id_inventario') or 0)
                    inventario = InventarioTerminado.query.get(id_inventario)
                    if not inventario:
                        raise ValueError('Inventario terminado no encontrado')

                    if not float(cantidad).is_integer():
                        raise ValueError('Para inventario terminado la cantidad debe ser un numero entero')

                    cantidad_inventario = int(cantidad)
                    if int(inventario.cantidad_disponible or 0) < cantidad_inventario:
                        raise ValueError('Stock insuficiente de inventario terminado para registrar merma')

                    producto = Producto.query.get(inventario.id_producto)
                    if not producto:
                        raise ValueError('Producto relacionado no encontrado')

                    porciones_base = int((producto.recetas[0].rendimiento_porciones if producto.recetas else 1) or 1)
                    costo_unitario = round(float(producto.precio or 0) / max(1, porciones_base), 2)
                    costo_perdida = round(cantidad_inventario * costo_unitario, 2)

                    autorizada = 1
                    id_usuario_autorizacion = None
                    if costo_perdida > MONTO_MAX_SIN_AUTORIZACION_ADMIN:
                        if int(getattr(current_user, 'id_rol', 0) or 0) != 1:
                            raise ValueError(
                                f'Merma mayor a ${MONTO_MAX_SIN_AUTORIZACION_ADMIN:.2f} requiere autorizacion Admin'
                            )
                        id_usuario_autorizacion = int(current_user.id_usuario)

                    inventario.cantidad_disponible = int(inventario.cantidad_disponible or 0) - cantidad_inventario
                    inventario.fecha_actualizacion = datetime.utcnow()

                    db.session.add(Merma(
                        tipo_articulo='InventarioTerminado',
                        articulo_id=id_inventario,
                        cantidad=float(cantidad_inventario),
                        motivo=motivo,
                        costo_perdida=round(costo_perdida, 2),
                        fecha_registro=datetime.utcnow(),
                        usuario_id=int(current_user.id_usuario),
                    ))

                    payload_log = {
                        'tipo_origen': 'InventarioTerminado',
                        'id_inventario': id_inventario,
                        'id_producto': producto.id_producto,
                        'cantidad': cantidad_inventario,
                        'costo_unitario': costo_unitario,
                        'costo_perdida': costo_perdida,
                        'motivo': motivo,
                        'observaciones': observaciones,
                        'id_usuario_registro': int(current_user.id_usuario),
                        'id_usuario_autorizacion': id_usuario_autorizacion,
                    }
                else:
                    raise ValueError('Tipo de merma invalido')

            db.session.commit()
            _registrar_log_merma_mongo(payload_log)
            flash('Merma registrada correctamente', 'success')
            return redirect(url_for('mermas.registrar'))

        except Exception as exc:
            db.session.rollback()
            flash(str(exc), 'danger')
            return redirect(url_for('mermas.registrar'))

    materias = (
        MateriaPrima.query
        .filter(MateriaPrima.estado.is_(True))
        .order_by(MateriaPrima.nombre.asc())
        .all()
    )
    inventarios = (
        db.session.query(InventarioTerminado, Producto)
        .join(Producto, Producto.id_producto == InventarioTerminado.id_producto)
        .filter(Producto.estado.is_(True))
        .order_by(Producto.nombre.asc())
        .all()
    )

    return render_template(
        'mermas/index.html',
        materias=materias,
        inventarios=inventarios,
        motivos=sorted(MOTIVOS_VALIDOS),
        monto_admin=MONTO_MAX_SIN_AUTORIZACION_ADMIN,
    )


@mermas.route('/historial', methods=['GET'])
@login_required
@role_required(1, 2, 3)
def historial():
    tipo_origen = (request.args.get('tipo_origen') or '').strip()
    motivo = (request.args.get('motivo') or '').strip()
    desde_raw = (request.args.get('desde') or '').strip()
    hasta_raw = (request.args.get('hasta') or '').strip()

    query = Merma.query.order_by(Merma.fecha_registro.desc())

    if tipo_origen in {'MateriaPrima', 'InventarioTerminado'}:
        query = query.filter(Merma.tipo_articulo == tipo_origen)

    motivo_normalizado = _normalizar_motivo_merma(motivo) if motivo else None
    if motivo_normalizado:
        query = query.filter(Merma.motivo == motivo_normalizado)

    if desde_raw:
        try:
            desde_dt = datetime.strptime(desde_raw, '%Y-%m-%d')
            query = query.filter(Merma.fecha_registro >= desde_dt)
        except ValueError:
            flash('Fecha desde invalida', 'warning')

    if hasta_raw:
        try:
            hasta_dt = datetime.strptime(hasta_raw, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Merma.fecha_registro < hasta_dt)
        except ValueError:
            flash('Fecha hasta invalida', 'warning')

    rows = query.limit(200).all()

    mongo_payload_by_key = {}
    mongo_db = _obtener_mongo_db()
    if mongo_db is not None:
        try:
            docs = list(
                mongo_db.bitacora_acciones.find(
                    {'modulo': 'seguridad.mermas'},
                    {'_id': 0, 'fecha': 1, 'payload_merma': 1},
                ).sort('fecha', -1).limit(500)
            )
            for doc in docs:
                payload = doc.get('payload_merma') or {}
                key = _merma_key_from_payload(payload)
                if key not in mongo_payload_by_key:
                    mongo_payload_by_key[key] = payload
        except Exception as exc:
            current_app.logger.warning(f'No se pudo leer historial de mermas en Mongo: {exc}')

    historial_rows = []
    total_perdidas = 0.0
    for row in rows:
        costo = float(row.costo_perdida or 0)
        total_perdidas += costo

        try:
            articulo_id = int(row.articulo_id) if row.articulo_id is not None else None
        except (TypeError, ValueError):
            articulo_id = None

        payload_key = _merma_payload_key(
            tipo_origen=row.tipo_articulo,
            articulo_id=articulo_id,
            cantidad=row.cantidad,
            costo_perdida=row.costo_perdida,
            motivo=row.motivo,
        )
        payload_mongo = mongo_payload_by_key.get(payload_key)
        observaciones = (payload_mongo.get('observaciones') or '').strip() if payload_mongo else ''

        if row.tipo_articulo == 'MateriaPrima':
            if articulo_id is None:
                item_nombre = 'Materia sin referencia'
            else:
                materia = MateriaPrima.query.get(articulo_id)
                item_nombre = materia.nombre if materia else f"Materia #{articulo_id}"
        else:
            if articulo_id is None:
                item_nombre = 'Inventario sin referencia'
            else:
                inventario = InventarioTerminado.query.get(articulo_id)
                producto = Producto.query.get(inventario.id_producto) if inventario else None
                item_nombre = producto.nombre if producto else f"Inventario #{articulo_id}"

        historial_rows.append(
            {
                'id_merma': row.id,
                'fecha': row.fecha_registro,
                'tipo_origen': row.tipo_articulo,
                'item_nombre': item_nombre,
                'cantidad': float(row.cantidad or 0),
                'costo_unitario': 0.0,
                'costo_perdida': costo,
                'motivo': row.motivo,
                'observaciones': observaciones,
                'autorizada': 1,
                'usuario_registro': row.usuario.username if row.usuario else row.usuario_id,
                'usuario_autorizacion': '-',
                'payload_mongo': payload_mongo,
            }
        )

    return render_template(
        'mermas/historial.html',
        historial_rows=historial_rows,
        total_registros=len(historial_rows),
        total_perdidas=total_perdidas,
        motivos=sorted(MOTIVOS_VALIDOS),
        filtro_tipo_origen=tipo_origen,
        filtro_motivo=motivo,
        filtro_desde=desde_raw,
        filtro_hasta=hasta_raw,
    )
