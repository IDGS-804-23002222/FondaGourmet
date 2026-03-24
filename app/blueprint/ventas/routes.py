from flask import Blueprint, request, jsonify
from app.extensions import db, app
from app.models import Venta, DetalleVenta

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/nueva', methods=['POST'])
def nueva_venta():
    nueva_venta = Venta(
        fecha=request.json['fecha'],
        total=request.json['total'],
        id_usuario=request.json['id_usuario']
    )
    db.session.add(nueva_venta)
    db.session.commit()
    for detalle in request.json['detalles']:
        nuevo_detalle = DetalleVenta(
            id_venta=nueva_venta.id_venta,
            id_producto=detalle['id_producto'],
            cantidad=detalle['cantidad'],
            precio_unitario=detalle['precio_unitario']
        )
        db.session.add(nuevo_detalle)
    db.session.commit()
    flash('Venta creada exitosamente', 'success')
    
    # Guardar ticket en MongoDB
    ticket = {
        'id_venta': nueva_venta.id_venta,
        'fecha': nueva_venta.fecha.strftime('%Y-%m-%d %H:%M:%S'),
        'total': nueva_venta.total,
        'id_usuario': nueva_venta.id_usuario,
        'detalles': request.json['detalles']
    }
    app.mongo.tickets.insert_one(ticket)
    
    # Guardar log de seguridad en MongoDB
    app.mongo.logs_seguridad.insert_one({
        'accion': 'Creación de venta',
        'id_usuario': nueva_venta.id_usuario,
        'fecha': nueva_venta.fecha.strftime('%d-%m-%Y %H:%M:%S'),
        'ip': request.remote_addr
    })
    
    return jsonify({'status': 'success', 'ticket_id': str(ticket['_id']), 'message': 'Venta creada exitosamente'}), 201

@ventas_bp.route('/<int:id_venta>', methods=['GET'])
def obtener_venta(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    detalles = DetalleVenta.query.filter_by(id_venta=id_venta).all()
    return jsonify({
        'id_venta': venta.id_venta,
        'fecha': venta.fecha.strftime('%Y-%m-%d %H:%M:%S'),
        'total': venta.total,
        'id_usuario': venta.id_usuario,
        'detalles': [
            {
                'id_producto': detalle.id_producto,
                'cantidad': detalle.cantidad,
                'precio_unitario': detalle.precio_unitario
            } for detalle in detalles
        ]
    })
    
@ventas_bp.route('/<int:id_venta>', methods=['DELETE'])
def eliminar_venta(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    db.session.delete(venta)
    db.session.commit()
    flash('Venta eliminada exitosamente', 'success')
    
    return jsonify({'message': 'Venta eliminada exitosamente'}), 200

@ventas_bp.route('/<int:id_venta>', methods=['PUT'])
def actualizar_venta(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    venta.fecha = request.json['fecha']
    venta.total = request.json['total']
    venta.id_usuario = request.json['id_usuario']
    db.session.commit()
    
    # Actualizar detalles
    DetalleVenta.query.filter_by(id_venta=id_venta).delete()  # Eliminar detalles antiguos
    for detalle in request.json['detalles']:
        nuevo_detalle = DetalleVenta(
            id_venta=id_venta,
            id_producto=detalle['id_producto'],
            cantidad=detalle['cantidad'],
            precio_unitario=detalle['precio_unitario']
        )
        db.session.add(nuevo_detalle)
    db.session.commit()
    
    flash('Venta actualizada exitosamente', 'success')
    
    return jsonify({'message': 'Venta actualizada exitosamente'}), 200

