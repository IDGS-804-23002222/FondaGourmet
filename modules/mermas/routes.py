import os
from datetime import datetime, timedelta

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import text
try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None

from models import InventarioTerminado, MateriaPrima, Producto, db
from utils.security import role_required
from . import mermas

MONTO_MAX_SIN_AUTORIZACION_ADMIN = 500.0
MOTIVOS_VALIDOS = {'Caducado', 'Danado', 'Error de Produccion', 'Robo'}


def _asegurar_tabla_mermas():
    existe = db.session.execute(
        text(
            """
            SELECT COUNT(*) AS total
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'mermas'
            """
        )
    ).mappings().first()
    return int((existe or {}).get('total', 0) or 0) > 0


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
    mongo_db = getattr(current_app, 'mongo', None)
    if mongo_db is not None:
        return mongo_db

    if MongoClient is None:
        return None

    uri = current_app.config.get('MONGO_URI') or os.getenv('MONGO_URI') or 'mongodb://localhost:27017/fondaGourmet'
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2500)
        default_db = client.get_default_database()
        return default_db if default_db is not None else client.get_database('fondaGourmet')
    except Exception:
        return None


@mermas.route('/', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def registrar():
    if not _asegurar_tabla_mermas():
        flash('La tabla mermas no existe. Ejecuta scripts/schema_mermas_ajustes.sql antes de usar este modulo.', 'warning')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        tipo_origen = (request.form.get('tipo_origen') or '').strip()
        motivo = (request.form.get('motivo') or '').strip()
        observaciones = (request.form.get('observaciones') or '').strip() or None

        try:
            cantidad = float((request.form.get('cantidad') or '0').strip())
        except Exception:
            flash('Cantidad invalida', 'danger')
            return redirect(url_for('mermas.registrar'))

        if cantidad <= 0:
            flash('La cantidad debe ser mayor a cero', 'danger')
            return redirect(url_for('mermas.registrar'))

        if motivo not in MOTIVOS_VALIDOS:
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

                    db.session.execute(
                        text(
                            """
                            INSERT INTO mermas (
                                tipo_origen, id_materia, id_producto, cantidad, costo_unitario, costo_perdida,
                                motivo, observaciones, autorizada, id_usuario_registro, id_usuario_autorizacion, fecha
                            ) VALUES (
                                'MateriaPrima', :id_materia, NULL, :cantidad, :costo_unitario, :costo_perdida,
                                :motivo, :observaciones, :autorizada, :id_usuario_registro, :id_usuario_autorizacion, :fecha
                            )
                            """
                        ),
                        {
                            'id_materia': id_materia,
                            'cantidad': cantidad,
                            'costo_unitario': costo_unitario,
                            'costo_perdida': costo_perdida,
                            'motivo': motivo,
                            'observaciones': observaciones,
                            'autorizada': autorizada,
                            'id_usuario_registro': int(current_user.id_usuario),
                            'id_usuario_autorizacion': id_usuario_autorizacion,
                            'fecha': datetime.now(),
                        },
                    )

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
                    if int(inventario.cantidad_disponible or 0) < int(cantidad):
                        raise ValueError('Stock insuficiente de inventario terminado para registrar merma')

                    producto = Producto.query.get(inventario.id_producto)
                    if not producto:
                        raise ValueError('Producto relacionado no encontrado')

                    porciones_base = int((producto.recetas[0].rendimiento_porciones if producto.recetas else 1) or 1)
                    costo_unitario = round(float(producto.precio or 0) / max(1, porciones_base), 2)
                    costo_perdida = round(cantidad * costo_unitario, 2)

                    autorizada = 1
                    id_usuario_autorizacion = None
                    if costo_perdida > MONTO_MAX_SIN_AUTORIZACION_ADMIN:
                        if int(getattr(current_user, 'id_rol', 0) or 0) != 1:
                            raise ValueError(
                                f'Merma mayor a ${MONTO_MAX_SIN_AUTORIZACION_ADMIN:.2f} requiere autorizacion Admin'
                            )
                        id_usuario_autorizacion = int(current_user.id_usuario)

                    inventario.cantidad_disponible = int(inventario.cantidad_disponible or 0) - int(cantidad)
                    inventario.fecha_actualizacion = datetime.utcnow()

                    # Compatibilidad con stock_actual legacy.
                    producto.stock_actual = float(inventario.cantidad_disponible)

                    db.session.execute(
                        text(
                            """
                            INSERT INTO mermas (
                                tipo_origen, id_inventario, id_producto, cantidad, costo_unitario, costo_perdida,
                                motivo, observaciones, autorizada, id_usuario_registro, id_usuario_autorizacion, fecha
                            ) VALUES (
                                'InventarioTerminado', :id_inventario, :id_producto, :cantidad, :costo_unitario, :costo_perdida,
                                :motivo, :observaciones, :autorizada, :id_usuario_registro, :id_usuario_autorizacion, :fecha
                            )
                            """
                        ),
                        {
                            'id_inventario': id_inventario,
                            'id_producto': producto.id_producto,
                            'cantidad': int(cantidad),
                            'costo_unitario': costo_unitario,
                            'costo_perdida': costo_perdida,
                            'motivo': motivo,
                            'observaciones': observaciones,
                            'autorizada': autorizada,
                            'id_usuario_registro': int(current_user.id_usuario),
                            'id_usuario_autorizacion': id_usuario_autorizacion,
                            'fecha': datetime.now(),
                        },
                    )

                    payload_log = {
                        'tipo_origen': 'InventarioTerminado',
                        'id_inventario': id_inventario,
                        'id_producto': producto.id_producto,
                        'cantidad': int(cantidad),
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
    if not _asegurar_tabla_mermas():
        flash('La tabla mermas no existe. Ejecuta scripts/schema_mermas_ajustes.sql antes de usar este modulo.', 'warning')
        return redirect(url_for('dashboard.index'))

    tipo_origen = (request.args.get('tipo_origen') or '').strip()
    motivo = (request.args.get('motivo') or '').strip()
    desde_raw = (request.args.get('desde') or '').strip()
    hasta_raw = (request.args.get('hasta') or '').strip()

    filters = []
    params = {}

    if tipo_origen in {'MateriaPrima', 'InventarioTerminado'}:
        filters.append('m.tipo_origen = :tipo_origen')
        params['tipo_origen'] = tipo_origen

    if motivo in MOTIVOS_VALIDOS:
        filters.append('m.motivo = :motivo')
        params['motivo'] = motivo

    if desde_raw:
        try:
            desde_dt = datetime.strptime(desde_raw, '%Y-%m-%d')
            filters.append('m.fecha >= :desde')
            params['desde'] = desde_dt
        except ValueError:
            flash('Fecha desde invalida', 'warning')

    if hasta_raw:
        try:
            hasta_dt = datetime.strptime(hasta_raw, '%Y-%m-%d') + timedelta(days=1)
            filters.append('m.fecha < :hasta')
            params['hasta'] = hasta_dt
        except ValueError:
            flash('Fecha hasta invalida', 'warning')

    where_clause = ''
    if filters:
        where_clause = 'WHERE ' + ' AND '.join(filters)

    rows = db.session.execute(
        text(
            f"""
            SELECT
                m.id_merma,
                m.fecha,
                m.tipo_origen,
                m.id_materia,
                m.id_inventario,
                m.id_producto,
                m.cantidad,
                m.costo_unitario,
                m.costo_perdida,
                m.motivo,
                m.observaciones,
                m.autorizada,
                m.id_usuario_registro,
                m.id_usuario_autorizacion,
                ur.username AS usuario_registro,
                ua.username AS usuario_autorizacion,
                mp.nombre AS materia_nombre,
                p.nombre AS producto_nombre
            FROM mermas m
            LEFT JOIN usuarios ur ON ur.id_usuario = m.id_usuario_registro
            LEFT JOIN usuarios ua ON ua.id_usuario = m.id_usuario_autorizacion
            LEFT JOIN materias_primas mp ON mp.id_materia = m.id_materia
            LEFT JOIN productos p ON p.id_producto = m.id_producto
            {where_clause}
            ORDER BY m.fecha DESC
            LIMIT 200
            """
        ),
        params,
    ).mappings().all()

    mongo_payload_by_obs = {}
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
                obs = (payload.get('observaciones') or '').strip()
                if obs and obs not in mongo_payload_by_obs:
                    mongo_payload_by_obs[obs] = payload
        except Exception as exc:
            current_app.logger.warning(f'No se pudo leer historial de mermas en Mongo: {exc}')

    historial_rows = []
    total_perdidas = 0.0
    for row in rows:
        costo = float(row.get('costo_perdida') or 0)
        total_perdidas += costo
        observaciones = (row.get('observaciones') or '').strip()
        payload_mongo = mongo_payload_by_obs.get(observaciones) if observaciones else None

        if row.get('tipo_origen') == 'MateriaPrima':
            item_nombre = row.get('materia_nombre') or f"Materia #{row.get('id_materia')}"
        else:
            item_nombre = row.get('producto_nombre') or f"Inventario #{row.get('id_inventario')}"

        historial_rows.append(
            {
                'id_merma': row.get('id_merma'),
                'fecha': row.get('fecha'),
                'tipo_origen': row.get('tipo_origen'),
                'item_nombre': item_nombre,
                'cantidad': float(row.get('cantidad') or 0),
                'costo_unitario': float(row.get('costo_unitario') or 0),
                'costo_perdida': costo,
                'motivo': row.get('motivo'),
                'observaciones': row.get('observaciones'),
                'autorizada': int(row.get('autorizada') or 0),
                'usuario_registro': row.get('usuario_registro') or row.get('id_usuario_registro'),
                'usuario_autorizacion': row.get('usuario_autorizacion') or row.get('id_usuario_autorizacion') or '-',
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
