from models import db, Compra, DetalleCompra, MateriaPrima, Proveedor, Produccion
from flask import current_app
from sqlalchemy import text
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def crear_solicitud_compra_desde_alerta(id_materia, id_usuario):
    try:
        materia = MateriaPrima.query.get(id_materia)

        if not materia:
            return None, "Materia prima no encontrada"

        if materia.stock_actual >= materia.stock_minimo:
            return None, "La materia prima ya no está por debajo del mínimo"

        cantidad = materia.stock_minimo - materia.stock_actual
        subtotal = cantidad * materia.precio

        compra = Compra(
            fecha=datetime.now(),
            total=subtotal,
            id_proveedor=materia.id_proveedor,
            id_usuario=id_usuario,
            estado="Solicitada"
        )

        db.session.add(compra)
        db.session.flush()

        db.session.add(DetalleCompra(
            id_compra=compra.id_compra,
            id_materia=materia.id_materia,
            cantidad=cantidad,
            precio_u=materia.precio,
            subtotal=subtotal
        ))

        db.session.commit()
        return compra.id_compra, f"Solicitud de compra creada para {materia.nombre}"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear solicitud de compra desde alerta: {str(e)}")
        return None, str(e)


def crear_solicitud_compra_manual(form, id_usuario):
    try:
        materias = form.getlist('id_materia[]')
        cantidades = form.getlist('cantidad[]')
        proveedores = form.getlist('id_proveedor[]')

        lineas = []

        for index, materia_id in enumerate(materias):
            if not materia_id:
                continue

            cantidad_raw = cantidades[index] if index < len(cantidades) else ''
            proveedor_raw = proveedores[index] if index < len(proveedores) else ''

            try:
                cantidad = float(cantidad_raw)
            except (TypeError, ValueError):
                return None, f"Cantidad inválida en la fila {index + 1}"

            if cantidad <= 0:
                return None, f"La cantidad debe ser mayor a cero en la fila {index + 1}"

            materia = MateriaPrima.query.get(int(materia_id))
            if not materia:
                return None, f"Materia prima no encontrada en la fila {index + 1}"

            proveedor_id = int(proveedor_raw) if proveedor_raw else materia.id_proveedor
            if proveedor_id != materia.id_proveedor:
                return None, f"El proveedor de la fila {index + 1} no corresponde a la materia prima seleccionada"
            proveedor = Proveedor.query.get(proveedor_id)
            if not proveedor:
                return None, f"Proveedor no encontrado en la fila {index + 1}"

            subtotal = cantidad * materia.precio

            lineas.append({
                'materia': materia,
                'cantidad': cantidad,
                'proveedor': proveedor,
                'subtotal': subtotal,
            })

        if not lineas:
            return None, "Agrega al menos una materia prima"

        compras_creadas = []
        lineas_por_proveedor = {}

        for linea in lineas:
            lineas_por_proveedor.setdefault(linea['proveedor'].id_proveedor, {
                'proveedor': linea['proveedor'],
                'lineas': []
            })['lineas'].append(linea)

        for grupo in lineas_por_proveedor.values():
            compra = Compra(
                fecha=datetime.now(),
                total=0,
                id_proveedor=grupo['proveedor'].id_proveedor,
                id_usuario=id_usuario,
                estado='Solicitada'
            )

            db.session.add(compra)
            db.session.flush()

            total_compra = 0

            for linea in grupo['lineas']:
                detalle = DetalleCompra(
                    id_compra=compra.id_compra,
                    id_materia=linea['materia'].id_materia,
                    cantidad=linea['cantidad'],
                    precio_u=linea['materia'].precio,
                    subtotal=linea['subtotal']
                )
                db.session.add(detalle)
                total_compra += linea['subtotal']

            compra.total = total_compra
            compras_creadas.append(compra)

        db.session.commit()

        if len(compras_creadas) == 1:
            return compras_creadas[0].id_compra, 'Solicitud de compra creada correctamente'

        return [compra.id_compra for compra in compras_creadas], f'Se crearon {len(compras_creadas)} solicitudes agrupadas por proveedor'

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear solicitud de compra manual: {str(e)}")
        return None, str(e)


def obtener_materias_faltantes_produccion(id_materia_prioritaria=None):
    sugerencias = {}

    producciones = Produccion.query.filter(Produccion.estado.in_(['Solicitada', 'En Proceso'])).all()

    for produccion in producciones:
        for detalle_prod in produccion.detalles:
            producto = detalle_prod.producto
            receta = producto.recetas[0] if producto and producto.recetas else None

            if not receta or receta.rendimiento <= 0:
                continue

            veces = detalle_prod.cantidad / receta.rendimiento

            for detalle_receta in receta.detalles:
                materia = detalle_receta.materia_prima
                if not materia:
                    continue

                requerido = detalle_receta.cantidad * veces
                faltante = max(0, requerido - materia.stock_actual)

                if faltante > 0:
                    if materia.id_materia not in sugerencias:
                        sugerencias[materia.id_materia] = {
                            'id_materia': materia.id_materia,
                            'cantidad_sugerida': 0,
                        }
                    sugerencias[materia.id_materia]['cantidad_sugerida'] += faltante

    if id_materia_prioritaria:
        materia_prioritaria = MateriaPrima.query.get(id_materia_prioritaria)
        if materia_prioritaria:
            faltante_minimo = max(0, materia_prioritaria.stock_minimo - materia_prioritaria.stock_actual)
            if id_materia_prioritaria not in sugerencias:
                sugerencias[id_materia_prioritaria] = {
                    'id_materia': id_materia_prioritaria,
                    'cantidad_sugerida': faltante_minimo if faltante_minimo > 0 else 1,
                }
            else:
                sugerencias[id_materia_prioritaria]['cantidad_sugerida'] = max(
                    sugerencias[id_materia_prioritaria]['cantidad_sugerida'],
                    faltante_minimo if faltante_minimo > 0 else 1
                )

    return list(sugerencias.values())


def obtener_materias_alerta_stock_bajo(id_materia_prioritaria=None):
    materias_alerta = (
        MateriaPrima.query
        .filter(MateriaPrima.stock_actual < MateriaPrima.stock_minimo)
        .order_by(MateriaPrima.nombre.asc())
        .all()
    )

    sugerencias = []
    for materia in materias_alerta:
        faltante = max(0, materia.stock_minimo - materia.stock_actual)
        sugerencias.append({
            'id_materia': materia.id_materia,
            'cantidad_sugerida': faltante if faltante > 0 else 1,
        })

    if id_materia_prioritaria:
        for index, item in enumerate(sugerencias):
            if item['id_materia'] == id_materia_prioritaria:
                sugerencias.insert(0, sugerencias.pop(index))
                break

    return sugerencias


def aplicar_cambios_compra(compra, form):
    total = 0

    for detalle in compra.detalles:
        precio = form.get(f"precio_{detalle.id_detalle}")

        if precio not in (None, ""):
            precio_normalizado = str(precio).replace(',', '.').strip()
            detalle.precio_u = float(precio_normalizado)

        detalle.subtotal = detalle.cantidad * detalle.precio_u

        if detalle.materia_prima:
            detalle.materia_prima.precio = detalle.precio_u

        total += detalle.subtotal

    compra.total = total

def obtener_compras():
    try:
        result = db.session.execute(text("""
    SELECT 
        c.id_compra,
        c.fecha,
        c.fecha_entrega,
        c.estado,
        u.username AS responsable,
        m.nombre AS nombre_materia,
        d.cantidad,
        m.stock_actual,
        m.stock_minimo,
        d.cantidad
    FROM compras c
    JOIN usuarios u ON c.id_usuario = u.id_usuario
    JOIN detalle_compra d ON c.id_compra = d.id_compra
    JOIN materias_primas m ON d.id_materia = m.id_materia
    WHERE c.estado IN ('Solicitada', 'En Proceso', 'Completada')
    ORDER BY c.fecha ASC
"""))

        compras_dict = {}

        for row in result.mappings():
            id_compra = row['id_compra']

            # Si la compra no existe, la creamos
            if id_compra not in compras_dict:
                compras_dict[id_compra] = {
                    'id_compra': id_compra,
                    'fecha': row['fecha'],
                    'fecha_entrega': row['fecha_entrega'],
                    'estado': row['estado'],
                    'responsable': row['responsable'],
                    'materias_primas': []
                    }
                
            if row['stock_actual'] < row['stock_minimo']:
                compras_dict[id_compra]['stock_suficiente'] = False

            # Agregamos materia prima a la compra
            compras_dict[id_compra]['materias_primas'].append({
                'nombre': row['nombre_materia'],
                'stock_actual': row['stock_actual'],
                'stock_minimo': row['stock_minimo'],
                'cantidad': row['cantidad']
            })

        compras = list(compras_dict.values())

        return compras, None

    except Exception as e:
        logger.error(f"Error al obtener compras: {str(e)}")
        return None, str(e)
    
def obtener_compra(id_compra):
    try:
        compra = Compra.query.get(id_compra)

        if not compra:
            return None, "Compra no encontrada"

        data = {
            "id": compra.id_compra,
            "fecha": compra.fecha,
            "fecha_entrega": compra.fecha_entrega,
            "estado": compra.estado,
            "id_proveedor": compra.id_proveedor,
            "metodo_pago": compra.metodo_pago,
            "total": compra.total,
            "materias_primas": []
        }

        for d in compra.detalles:
            materia = d.materia_prima

            data["materias_primas"].append({
                "id_detalle": d.id_detalle,
                "id_materia": materia.id_materia,
                "nombre": materia.nombre,
                "cantidad": d.cantidad,
                "precio_unitario": d.precio_u,  # 🔥 CORRECTO
                "subtotal": d.subtotal,
                "stock_actual": materia.stock_actual
            })

        return data, None

    except Exception as e:
        return None, str(e)
        
def completar_compra(id_compra, form=None):
    try:
        compra = Compra.query.get(id_compra)

        if not compra:
            return False, "Compra no encontrada"

        if compra.estado == "Completada":
            return False, "Ya fue completada"

        if form is not None:
            aplicar_cambios_compra(compra, form)

        for detalle in compra.detalles:
            materia = detalle.materia_prima
            materia.stock_actual += detalle.cantidad

        compra.estado = "Completada"
        if not compra.fecha_entrega:
            compra.fecha_entrega = datetime.now()

        db.session.commit()

        return True, "Compra completada correctamente"

    except Exception as e:
        db.session.rollback()
        return False, str(e)