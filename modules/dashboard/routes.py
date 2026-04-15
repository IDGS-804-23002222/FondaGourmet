import os
from datetime import datetime, timedelta

from flask import current_app, render_template
from flask_login import login_required
from sqlalchemy import text

from models import Caja as CajaModel
from models import Cliente, MovimientoCaja, Pedido, Persona, db
from utils.security import role_required
from . import dashboard

try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None


@dashboard.route('/', methods=['GET', 'POST'])
@login_required
@role_required(1, 3)
def index():
    ahora = datetime.now()
    inicio_hoy = datetime.combine(ahora.date(), datetime.min.time())
    fin_hoy = inicio_hoy + timedelta(days=1)
    inicio_semana = inicio_hoy - timedelta(days=6)
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # SQL: ingresos hoy, pedidos pendientes y ticket promedio
    resumen_sql = db.session.execute(
        text(
            """
            SELECT
                COALESCE(SUM(CASE WHEN p.estado_pago = 'Pagado' THEN p.total ELSE 0 END), 0) AS ingresos_hoy,
                COALESCE(SUM(CASE WHEN p.estado_pago = 'Pagado' THEN 1 ELSE 0 END), 0) AS pedidos_totales_hoy,
                COALESCE(AVG(CASE WHEN p.estado_pago = 'Pagado' THEN p.total ELSE NULL END), 0) AS ticket_promedio,
                COALESCE(SUM(CASE WHEN p.estado_pago = 'Pendiente' AND p.estado <> 'Cancelado' THEN 1 ELSE 0 END), 0) AS pedidos_pendientes
            FROM pedidos p
            WHERE COALESCE(p.fecha_entrega, p.fecha) >= :inicio_hoy
              AND COALESCE(p.fecha_entrega, p.fecha) < :fin_hoy
            """
        ),
        {'inicio_hoy': inicio_hoy, 'fin_hoy': fin_hoy},
    ).mappings().first()

    ingresos_hoy = float((resumen_sql or {}).get('ingresos_hoy', 0) or 0)
    pedidos_totales_hoy = int((resumen_sql or {}).get('pedidos_totales_hoy', 0) or 0)
    ticket_promedio = float((resumen_sql or {}).get('ticket_promedio', 0) or 0)
    pedidos_pendientes = int((resumen_sql or {}).get('pedidos_pendientes', 0) or 0)

    # SQL: clientes nuevos hoy
    clientes_nuevos = (
        db.session.query(db.func.count(Cliente.id_cliente))
        .join(Persona, Persona.id_persona == Cliente.id_persona)
        .filter(Persona.fecha_creacion >= inicio_hoy, Persona.fecha_creacion < fin_hoy)
        .scalar()
        or 0
    )

    # SQL: balance en caja (sesion abierta)
    caja_abierta = CajaModel.query.filter_by(estado='Abierta').order_by(CajaModel.fecha.desc()).first()
    balance_caja = 0.0
    if caja_abierta:
        inicio_caja = caja_abierta.fecha
        fin_caja = ahora + timedelta(seconds=5)

        total_efectivo = db.session.execute(
            text(
                """
                SELECT COALESCE(SUM(p.total), 0) AS total_efectivo
                FROM pedidos p
                LEFT JOIN pedidos_meta pm ON pm.id_pedido = p.id_pedido
                WHERE p.estado_pago = 'Pagado'
                  AND COALESCE(pm.metodo_pago, 'Efectivo') = 'Efectivo'
                  AND COALESCE(p.fecha_entrega, p.fecha) >= :inicio_caja
                  AND COALESCE(p.fecha_entrega, p.fecha) < :fin_caja
                """
            ),
            {'inicio_caja': inicio_caja, 'fin_caja': fin_caja},
        ).mappings().first()

        egresos_caja = (
            db.session.query(db.func.sum(MovimientoCaja.monto))
            .filter(MovimientoCaja.id_caja == caja_abierta.id_caja, MovimientoCaja.tipo == 'Egreso')
            .scalar()
            or 0
        )

        balance_caja = float(caja_abierta.monto_inicial or 0) + float((total_efectivo or {}).get('total_efectivo', 0) or 0) - float(egresos_caja or 0)

    # SQL: ventas por dia ultima semana (Chart.js)
    ventas_semana_rows = db.session.execute(
        text(
            """
            SELECT DATE(COALESCE(p.fecha_entrega, p.fecha)) AS dia,
                   COALESCE(SUM(p.total), 0) AS total
            FROM pedidos p
            WHERE p.estado_pago = 'Pagado'
              AND COALESCE(p.fecha_entrega, p.fecha) >= :inicio_semana
              AND COALESCE(p.fecha_entrega, p.fecha) < :fin_hoy
            GROUP BY DATE(COALESCE(p.fecha_entrega, p.fecha))
            ORDER BY dia ASC
            """
        ),
        {'inicio_semana': inicio_semana, 'fin_hoy': fin_hoy},
    ).mappings().all()

    mapa_semana = {str(row['dia']): float(row['total'] or 0) for row in ventas_semana_rows}
    chart_labels = []
    chart_data = []
    for i in range(7):
        dia = (inicio_semana + timedelta(days=i)).date()
        chart_labels.append(dia.strftime('%d/%m'))
        chart_data.append(mapa_semana.get(str(dia), 0.0))

    # SQL: total de perdidas del mes (si existe tabla mermas)
    total_perdidas_mes = 0.0
    mermas_mes = 0
    try:
        merma_sql = db.session.execute(
            text(
                """
                SELECT
                    COALESCE(SUM(m.costo_perdida), 0) AS total_perdidas_mes,
                    COALESCE(COUNT(m.id_merma), 0) AS mermas_mes
                FROM mermas m
                WHERE m.fecha >= :inicio_mes
                  AND m.fecha < :fin_hoy
                """
            ),
            {'inicio_mes': inicio_mes, 'fin_hoy': fin_hoy},
        ).mappings().first()
        total_perdidas_mes = float((merma_sql or {}).get('total_perdidas_mes', 0) or 0)
        mermas_mes = int((merma_sql or {}).get('mermas_mes', 0) or 0)
    except Exception:
        total_perdidas_mes = 0.0
        mermas_mes = 0

    # Mongo: ultimos 10 logs para actividad reciente
    logs_feed = []
    mongo_db = getattr(current_app, 'mongo', None)

    if mongo_db is None and MongoClient is not None:
        uri = current_app.config.get('MONGO_URI') or os.getenv('MONGO_URI') or 'mongodb://localhost:27017/fondaGourmet'
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2500)
            db_default = client.get_default_database()
            mongo_db = db_default if db_default is not None else client.get_database('fondaGourmet')
            client.admin.command('ping')
        except Exception:
            mongo_db = None

    if mongo_db is not None:
        try:
            docs = list(mongo_db.logs.find({}, {'_id': 0}).sort('fecha', -1).limit(10))
            if not docs and 'bitacora_acciones' in mongo_db.list_collection_names():
                docs = list(mongo_db.bitacora_acciones.find({}, {'_id': 0}).sort('fecha', -1).limit(10))

            for doc in docs:
                fecha = doc.get('fecha')
                if isinstance(fecha, str):
                    fecha_fmt = fecha
                elif fecha is None:
                    fecha_fmt = '-'
                else:
                    fecha_fmt = fecha.strftime('%d/%m/%Y %H:%M')

                logs_feed.append({
                    'fecha': fecha_fmt,
                    'accion': doc.get('accion') or doc.get('metodo') or doc.get('endpoint') or 'actividad',
                    'descripcion': doc.get('descripcion') or doc.get('ruta') or '-',
                    'usuario': doc.get('id_usuario') or doc.get('usuario') or '-',
                    'ip': doc.get('ip') or '-',
                })
        except Exception:
            logs_feed = []

    return render_template(
        'dashboard/index.html',
        ingresos_hoy=ingresos_hoy,
        pedidos_totales_hoy=pedidos_totales_hoy,
        pedidos_pendientes=pedidos_pendientes,
        ticket_promedio=ticket_promedio,
        clientes_nuevos=int(clientes_nuevos),
        balance_caja=balance_caja,
        chart_labels=chart_labels,
        chart_data=chart_data,
        total_perdidas_mes=total_perdidas_mes,
        mermas_mes=mermas_mes,
        logs_feed=logs_feed,
        caja_abierta=bool(caja_abierta),
    )

