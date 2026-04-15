import uuid

from flask import current_app, jsonify, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from models import db
from mongo_models import guardar_log
from utils.security import role_required
from . import clientes_bp


def _normalize_name(nombre_completo):
    partes = [parte for parte in (nombre_completo or '').strip().split(' ') if parte]
    if not partes:
        return None, None, None

    if len(partes) == 1:
        return partes[0], 'N/A', None

    nombre = partes[0]
    apellido_p = partes[1]
    apellido_m = ' '.join(partes[2:]) if len(partes) > 2 else None
    return nombre, apellido_p, apellido_m


def _ensure_schema():
    try:
        db.session.execute(text("ALTER TABLE personas ADD COLUMN rfc_tax_id VARCHAR(20) NULL"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE clientes ADD COLUMN estado_activo TINYINT(1) NOT NULL DEFAULT 1"))
        db.session.commit()
    except Exception:
        db.session.rollback()


@clientes_bp.route('/')
@login_required
@role_required(1, 3)
def index():
    _ensure_schema()
    return render_template('clientes/index.html')


@clientes_bp.route('/api/list', methods=['GET'])
@login_required
@role_required(1, 3)
def list_clientes():
    _ensure_schema()
    q = (request.args.get('q') or '').strip()
    estado = (request.args.get('estado') or 'all').strip().lower()

    filtros = []
    params = {}

    if q:
        filtros.append(
            "(CONCAT_WS(' ', p.nombre, p.apellido_p, p.apellido_m) LIKE :q OR p.correo LIKE :q OR p.telefono LIKE :q OR COALESCE(p.rfc_tax_id,'') LIKE :q)"
        )
        params['q'] = f'%{q}%'

    if estado in ('activo', 'inactivo'):
        filtros.append('c.estado_activo = :estado')
        params['estado'] = 1 if estado == 'activo' else 0

    where_clause = ''
    if filtros:
        where_clause = 'WHERE ' + ' AND '.join(filtros)

    sql = f"""
        SELECT
            c.id_cliente,
            p.nombre,
            p.apellido_p,
            p.apellido_m,
            p.telefono,
            p.correo,
            COALESCE(p.rfc_tax_id, '') AS rfc_tax_id,
            p.fecha_creacion AS fecha_registro,
            c.estado_activo,
            COUNT(pe.id_pedido) AS total_pedidos
        FROM clientes c
        INNER JOIN personas p ON p.id_persona = c.id_persona
        INNER JOIN usuarios u ON u.id_usuario = c.id_usuario
        LEFT JOIN pedidos pe ON pe.id_cliente = c.id_cliente
        {where_clause}
        GROUP BY c.id_cliente, p.nombre, p.apellido_p, p.apellido_m, p.telefono, p.correo, p.rfc_tax_id, p.fecha_creacion, c.estado_activo
        ORDER BY p.fecha_creacion DESC
    """

    try:
        rows = db.session.execute(text(sql), params).mappings().all()
        payload = []
        for row in rows:
            nombre = ' '.join(
                parte for parte in [row['nombre'], row['apellido_p'], row['apellido_m']] if parte and str(parte).strip()
            )
            payload.append({
                'id_cliente': row['id_cliente'],
                'nombre': nombre,
                'telefono': row['telefono'],
                'correo': row['correo'],
                'rfc_tax_id': row['rfc_tax_id'] or '',
                'fecha_registro': row['fecha_registro'].strftime('%Y-%m-%d %H:%M') if row['fecha_registro'] else '',
                'estado_bool': bool(row['estado_activo']),
                'estado_display': 'Activo' if row['estado_activo'] else 'Inactivo',
                'total_pedidos': int(row['total_pedidos'] or 0),
            })

        return jsonify({'success': True, 'clientes': payload})
    except Exception as exc:
        current_app.logger.error(f'Error listando clientes: {exc}')
        return jsonify({'success': False, 'message': 'No se pudieron cargar los clientes'}), 500


@clientes_bp.route('/api/create', methods=['POST'])
@login_required
@role_required(1, 3)
def create_cliente():
    _ensure_schema()
    data = request.get_json(silent=True) or {}

    nombre_completo = (data.get('nombre') or '').strip()
    telefono = (data.get('telefono') or '').strip()
    correo = (data.get('correo') or '').strip().lower()
    rfc_tax_id = (data.get('rfc_tax_id') or '').strip().upper() or None

    nombre, apellido_p, apellido_m = _normalize_name(nombre_completo)
    if not nombre:
        return jsonify({'success': False, 'message': 'El nombre es obligatorio'}), 400
    if not telefono:
        return jsonify({'success': False, 'message': 'El teléfono es obligatorio'}), 400
    if not correo:
        return jsonify({'success': False, 'message': 'El correo es obligatorio'}), 400

    try:
        rol_cliente = db.session.execute(
            text("SELECT id_rol FROM roles WHERE LOWER(nombre) = 'cliente' LIMIT 1")
        ).scalar()
        if not rol_cliente:
            return jsonify({'success': False, 'message': 'No existe el rol Cliente configurado'}), 400

        existing = db.session.execute(
            text("SELECT id_persona FROM personas WHERE telefono = :telefono OR correo = :correo LIMIT 1"),
            {'telefono': telefono, 'correo': correo},
        ).scalar()
        if existing:
            return jsonify({'success': False, 'message': 'Ya existe un cliente con ese teléfono o correo'}), 409

        db.session.execute(
            text(
                """
                INSERT INTO personas (nombre, apellido_p, apellido_m, telefono, correo, direccion, rfc_tax_id, fecha_creacion)
                VALUES (:nombre, :apellido_p, :apellido_m, :telefono, :correo, :direccion, :rfc_tax_id, NOW())
                """
            ),
            {
                'nombre': nombre,
                'apellido_p': apellido_p,
                'apellido_m': apellido_m,
                'telefono': telefono,
                'correo': correo,
                'direccion': 'N/D',
                'rfc_tax_id': rfc_tax_id,
            },
        )

        id_persona = db.session.execute(text('SELECT LAST_INSERT_ID()')).scalar()

        username = f"cli_{str(uuid.uuid4())[:8]}"
        password_hash = generate_password_hash(str(uuid.uuid4()))
        fs_uniquifier = str(uuid.uuid4())

        db.session.execute(
            text(
                """
                INSERT INTO usuarios (username, contrasena, estado, fs_uniquifier, fecha_creacion, id_rol)
                VALUES (:username, :contrasena, 1, :fs_uniquifier, NOW(), :id_rol)
                """
            ),
            {
                'username': username,
                'contrasena': password_hash,
                'fs_uniquifier': fs_uniquifier,
                'id_rol': rol_cliente,
            },
        )

        id_usuario = db.session.execute(text('SELECT LAST_INSERT_ID()')).scalar()

        db.session.execute(
            text('INSERT INTO clientes (id_usuario, id_persona, estado_activo) VALUES (:id_usuario, :id_persona, 1)'),
            {'id_usuario': id_usuario, 'id_persona': id_persona},
        )

        id_cliente = db.session.execute(text('SELECT LAST_INSERT_ID()')).scalar()
        db.session.commit()

        guardar_log(
            current_app,
            action='cliente_creado',
            descripcion=f'Cliente #{id_cliente} creado por usuario #{current_user.id_usuario}',
            id_usuario=current_user.id_usuario,
            ip=request.remote_addr,
        )

        return jsonify({'success': True, 'message': 'Cliente creado correctamente', 'id_cliente': id_cliente})
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Error creando cliente: {exc}')
        return jsonify({'success': False, 'message': 'No se pudo crear el cliente'}), 500


@clientes_bp.route('/api/<int:id_cliente>', methods=['GET'])
@login_required
@role_required(1, 3)
def get_cliente(id_cliente):
    _ensure_schema()
    try:
        row = db.session.execute(
            text(
                """
                SELECT c.id_cliente, p.nombre, p.apellido_p, p.apellido_m, p.telefono, p.correo,
                      COALESCE(p.rfc_tax_id, '') AS rfc_tax_id, c.estado_activo
                FROM clientes c
                INNER JOIN personas p ON p.id_persona = c.id_persona
                INNER JOIN usuarios u ON u.id_usuario = c.id_usuario
                WHERE c.id_cliente = :id_cliente
                LIMIT 1
                """
            ),
            {'id_cliente': id_cliente},
        ).mappings().first()

        if not row:
            return jsonify({'success': False, 'message': 'Cliente no encontrado'}), 404

        nombre = ' '.join(
            parte for parte in [row['nombre'], row['apellido_p'], row['apellido_m']] if parte and str(parte).strip()
        )

        return jsonify(
            {
                'success': True,
                'cliente': {
                    'id_cliente': row['id_cliente'],
                    'nombre': nombre,
                    'telefono': row['telefono'],
                    'correo': row['correo'],
                    'rfc_tax_id': row['rfc_tax_id'] or '',
                    'estado_bool': bool(row['estado_activo']),
                },
            }
        )
    except Exception as exc:
        current_app.logger.error(f'Error obteniendo cliente: {exc}')
        return jsonify({'success': False, 'message': 'No se pudo obtener el cliente'}), 500


@clientes_bp.route('/api/<int:id_cliente>/update', methods=['POST'])
@login_required
@role_required(1, 3)
def update_cliente(id_cliente):
    _ensure_schema()
    data = request.get_json(silent=True) or {}

    nombre_completo = (data.get('nombre') or '').strip()
    telefono = (data.get('telefono') or '').strip()
    correo = (data.get('correo') or '').strip().lower()
    rfc_tax_id = (data.get('rfc_tax_id') or '').strip().upper() or None

    nombre, apellido_p, apellido_m = _normalize_name(nombre_completo)
    if not nombre:
        return jsonify({'success': False, 'message': 'El nombre es obligatorio'}), 400
    if not telefono:
        return jsonify({'success': False, 'message': 'El teléfono es obligatorio'}), 400
    if not correo:
        return jsonify({'success': False, 'message': 'El correo es obligatorio'}), 400

    try:
        row = db.session.execute(
            text('SELECT id_persona FROM clientes WHERE id_cliente = :id_cliente LIMIT 1'),
            {'id_cliente': id_cliente},
        ).mappings().first()

        if not row:
            return jsonify({'success': False, 'message': 'Cliente no encontrado'}), 404

        id_persona = row['id_persona']

        conflict = db.session.execute(
            text(
                """
                SELECT id_persona
                FROM personas
                WHERE id_persona <> :id_persona
                  AND (telefono = :telefono OR correo = :correo)
                LIMIT 1
                """
            ),
            {'id_persona': id_persona, 'telefono': telefono, 'correo': correo},
        ).scalar()

        if conflict:
            return jsonify({'success': False, 'message': 'Ya existe otro cliente con ese teléfono o correo'}), 409

        db.session.execute(
            text(
                """
                UPDATE personas
                SET nombre = :nombre,
                    apellido_p = :apellido_p,
                    apellido_m = :apellido_m,
                    telefono = :telefono,
                    correo = :correo,
                    rfc_tax_id = :rfc_tax_id
                WHERE id_persona = :id_persona
                """
            ),
            {
                'nombre': nombre,
                'apellido_p': apellido_p,
                'apellido_m': apellido_m,
                'telefono': telefono,
                'correo': correo,
                'rfc_tax_id': rfc_tax_id,
                'id_persona': id_persona,
            },
        )

        db.session.commit()

        guardar_log(
            current_app,
            action='cliente_editado',
            descripcion=f'Cliente #{id_cliente} editado por usuario #{current_user.id_usuario}',
            id_usuario=current_user.id_usuario,
            ip=request.remote_addr,
        )

        return jsonify({'success': True, 'message': 'Cliente actualizado correctamente'})
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Error actualizando cliente: {exc}')
        return jsonify({'success': False, 'message': 'No se pudo actualizar el cliente'}), 500


@clientes_bp.route('/api/<int:id_cliente>/toggle-status', methods=['POST'])
@login_required
@role_required(1, 3)
def toggle_cliente_status(id_cliente):
    try:
        row = db.session.execute(
            text('SELECT id_usuario FROM clientes WHERE id_cliente = :id_cliente LIMIT 1'),
            {'id_cliente': id_cliente},
        ).mappings().first()

        if not row:
            return jsonify({'success': False, 'message': 'Cliente no encontrado'}), 404

        id_usuario = row['id_usuario']

        estado_actual = db.session.execute(
            text('SELECT estado_activo FROM clientes WHERE id_cliente = :id_cliente LIMIT 1'),
            {'id_cliente': id_cliente},
        ).scalar()

        if estado_actual is None:
            return jsonify({'success': False, 'message': 'Cliente no encontrado'}), 404

        nuevo_estado = 0 if int(estado_actual) == 1 else 1

        db.session.execute(
            text('UPDATE clientes SET estado_activo = :estado WHERE id_cliente = :id_cliente'),
            {'estado': nuevo_estado, 'id_cliente': id_cliente},
        )
        db.session.execute(
            text('UPDATE usuarios SET estado = :estado WHERE id_usuario = :id_usuario'),
            {'estado': nuevo_estado, 'id_usuario': id_usuario},
        )
        db.session.commit()

        guardar_log(
            current_app,
            action='cliente_estado_actualizado',
            descripcion=f'Cliente #{id_cliente} cambiado a {"Activo" if nuevo_estado else "Inactivo"} por usuario #{current_user.id_usuario}',
            id_usuario=current_user.id_usuario,
            ip=request.remote_addr,
        )

        return jsonify(
            {
                'success': True,
                'message': 'Cliente activado' if nuevo_estado else 'Cliente desactivado',
                'estado': 'Activo' if nuevo_estado else 'Inactivo',
            }
        )
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Error cambiando estado del cliente: {exc}')
        return jsonify({'success': False, 'message': 'No se pudo cambiar el estado'}), 500
