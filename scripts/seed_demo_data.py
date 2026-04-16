#!/usr/bin/env python3
"""Seed realistic demo data for end-to-end manual testing.

Idempotent: creates missing entities and reuses existing ones when possible.
"""

from datetime import datetime, timedelta
import uuid
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from werkzeug.security import generate_password_hash

from app import create_app
from models import (
    db,
    Rol,
    Persona,
    Usuario,
    Cliente,
    Proveedor,
    CategoriaProveedor,
    CategoriaIngrediente,
    CategoriaPlatillo,
    MateriaPrima,
    Producto,
    InventarioTerminado,
    Pedido,
    PedidoMeta,
    DetallePedido,
    Produccion,
    DetalleProduccion,
)


def _get_or_create_role(nombre):
    role = Rol.query.filter_by(nombre=nombre).first()
    if role:
        return role
    role = Rol(nombre=nombre)
    db.session.add(role)
    db.session.flush()
    return role


def _get_or_create_persona(nombre, apellido_p, telefono, correo, direccion='Centro'):
    p = Persona.query.filter_by(correo=correo).first()
    if p:
        return p
    p = Persona(
        nombre=nombre,
        apellido_p=apellido_p,
        apellido_m='',
        telefono=telefono,
        correo=correo,
        direccion=direccion,
    )
    db.session.add(p)
    db.session.flush()
    return p


def _get_or_create_user(username, password, role, persona=None):
    user = Usuario.query.filter_by(username=username).first()
    if user:
        return user

    user = Usuario(
        username=username,
        contrasena=generate_password_hash(password),
        estado=True,
        fs_uniquifier=str(uuid.uuid4()),
        id_rol=role.id_rol,
    )
    db.session.add(user)
    db.session.flush()

    if role.nombre == 'Cliente' and persona:
        cliente = Cliente.query.filter_by(id_persona=persona.id_persona).first()
        if not cliente:
            cliente = Cliente(id_usuario=user.id_usuario, id_persona=persona.id_persona)
            db.session.add(cliente)
            db.session.flush()

    return user


def _get_or_create_categoria(model_cls, nombre):
    row = model_cls.query.filter_by(nombre=nombre).first()
    if row:
        return row
    row = model_cls(nombre=nombre, descripcion=f'Categoria {nombre}', estado=True)
    db.session.add(row)
    db.session.flush()
    return row


def _get_or_create_proveedor(nombre='Comercial Centro'):
    correo = 'proveedor.demo@fondagourmet.local'
    persona = _get_or_create_persona(nombre, 'Demo', '5511112222', correo, 'Zona Centro')
    categoria = _get_or_create_categoria(CategoriaProveedor, 'Abarrotes')

    proveedor = Proveedor.query.filter_by(id_persona=persona.id_persona).first()
    if proveedor:
        return proveedor

    proveedor = Proveedor(
        id_persona=persona.id_persona,
        id_categoria_proveedor=categoria.id_categoria_proveedor,
        estado=True,
    )
    db.session.add(proveedor)
    db.session.flush()
    return proveedor


def _get_or_create_materia(nombre, proveedor, precio, stock):
    categoria = _get_or_create_categoria(CategoriaIngrediente, 'Proteinas')
    materia = MateriaPrima.query.filter_by(nombre=nombre).first()
    if materia:
        materia.precio = float(precio)
        materia.stock_actual = float(max(materia.stock_actual or 0, stock))
        return materia

    materia = MateriaPrima(
        nombre=nombre,
        unidad_medida='kg',
        stock_actual=float(stock),
        stock_minimo=2,
        precio=float(precio),
        porcentaje_merma=3,
        factor_conversion=1,
        estado=True,
        id_categoria_ingrediente=categoria.id_categoria_ingrediente,
        id_proveedor=proveedor.id_proveedor,
    )
    db.session.add(materia)
    db.session.flush()
    return materia


def _get_or_create_producto(nombre, precio, dias_duracion=3):
    categoria = _get_or_create_categoria(CategoriaPlatillo, 'Platos fuertes')
    producto = Producto.query.filter_by(nombre=nombre).first()
    if producto:
        producto.precio = float(precio)
        producto.estado = True
        if not producto.dias_duracion or producto.dias_duracion < 2:
            producto.dias_duracion = dias_duracion
        return producto

    producto = Producto(
        nombre=nombre,
        descripcion=f'{nombre} preparado al momento',
        precio=float(precio),
        stock_minimo=2,
        fecha_produccion=datetime.utcnow(),
        dias_duracion=max(2, int(dias_duracion)),
        estado=True,
        id_categoria_platillo=categoria.id_categoria_platillo,
    )
    db.session.add(producto)
    db.session.flush()
    return producto


def _ensure_inventario(producto, cantidad):
    inventario = InventarioTerminado.query.filter_by(id_producto=producto.id_producto).first()
    if inventario:
        inventario.cantidad_disponible = max(int(inventario.cantidad_disponible or 0), int(cantidad))
        inventario.fecha_actualizacion = datetime.utcnow()
        return inventario

    inventario = InventarioTerminado(
        id_producto=producto.id_producto,
        cantidad_disponible=int(cantidad),
        fecha_actualizacion=datetime.utcnow(),
    )
    db.session.add(inventario)
    db.session.flush()
    return inventario


def _create_demo_pedido(cliente, usuario_responsable, items, estado='Pendiente', estado_pago='Pendiente', metodo_pago='Efectivo', requiere_produccion=False):
    total = sum(float(p.precio) * int(c) for p, c in items)
    pedido = Pedido(
        fecha=datetime.utcnow(),
        fecha_entrega=(datetime.utcnow() + timedelta(hours=2)) if estado in ('Completado', 'Producido') else None,
        estado=estado,
        estado_pago=estado_pago,
        id_cliente=cliente.id_cliente,
        requiere_produccion=bool(requiere_produccion),
        total=round(total, 2),
    )
    db.session.add(pedido)
    db.session.flush()

    meta = PedidoMeta(
        id_pedido=pedido.id_pedido,
        metodo_pago=metodo_pago,
        id_usuario=usuario_responsable.id_usuario,
    )
    db.session.add(meta)

    for producto, cantidad in items:
        db.session.add(DetallePedido(
            id_pedido=pedido.id_pedido,
            id_producto=producto.id_producto,
            cantidad=int(cantidad),
            subtotal=round(float(producto.precio) * int(cantidad), 2),
            atendido=estado in ('Completado', 'Producido'),
            en_produccion=estado == 'En Proceso',
        ))

    if estado == 'En Proceso':
        produccion = Produccion(
            fecha_solicitud=datetime.utcnow(),
            fecha_necesaria=datetime.utcnow() + timedelta(days=1),
            estado='Solicitada',
            id_pedido=pedido.id_pedido,
            id_usuario=usuario_responsable.id_usuario,
        )
        db.session.add(produccion)
        db.session.flush()
        for producto, cantidad in items:
            db.session.add(DetalleProduccion(
                id_produccion=produccion.id_produccion,
                id_producto=producto.id_producto,
                id_materia=None,
                cantidad=float(cantidad),
            ))

    return pedido


def run():
    app = create_app()
    with app.app_context():
        # Roles base
        rol_admin = _get_or_create_role('Administrador')
        rol_cajero = _get_or_create_role('Cajero')
        rol_cocinero = _get_or_create_role('Cocinero')
        rol_cliente = _get_or_create_role('Cliente')

        # Usuarios demo
        p_admin = _get_or_create_persona('Ana', 'Admin', '5510000001', 'ana.admin@fondagourmet.local')
        p_cajero = _get_or_create_persona('Carlos', 'Caja', '5510000002', 'carlos.caja@fondagourmet.local')
        p_cocinero = _get_or_create_persona('Luis', 'Cocina', '5510000003', 'luis.cocina@fondagourmet.local')
        p_cli1 = _get_or_create_persona('Mariana', 'Lopez', '5510000004', 'mariana.lopez@fondagourmet.local')
        p_cli2 = _get_or_create_persona('Jorge', 'Santos', '5510000005', 'jorge.santos@fondagourmet.local')

        u_admin = _get_or_create_user('demo_admin', 'DemoAdmin123!', rol_admin, p_admin)
        u_cajero = _get_or_create_user('demo_cajero', 'DemoCaja123!', rol_cajero, p_cajero)
        _get_or_create_user('demo_cocinero', 'DemoCocina123!', rol_cocinero, p_cocinero)
        u_cli1 = _get_or_create_user('demo_cliente1', 'DemoCliente123!', rol_cliente, p_cli1)
        u_cli2 = _get_or_create_user('demo_cliente2', 'DemoCliente123!', rol_cliente, p_cli2)

        c_cli1 = Cliente.query.filter_by(id_usuario=u_cli1.id_usuario).first()
        c_cli2 = Cliente.query.filter_by(id_usuario=u_cli2.id_usuario).first()

        # Inventario demo
        proveedor = _get_or_create_proveedor()
        _get_or_create_materia('Pollo fresco', proveedor, precio=115.0, stock=32)
        _get_or_create_materia('Arroz premium', proveedor, precio=39.0, stock=54)
        _get_or_create_materia('Verdura mixta', proveedor, precio=48.5, stock=27)

        p1 = _get_or_create_producto('Pechuga a la plancha', 95.0)
        p2 = _get_or_create_producto('Arroz con verduras', 72.0)
        p3 = _get_or_create_producto('Ensalada de la casa', 58.0)

        _ensure_inventario(p1, 25)
        _ensure_inventario(p2, 30)
        _ensure_inventario(p3, 20)

        # Pedidos demo (evitar duplicados excesivos)
        pedidos_demo_existentes = Pedido.query.filter(Pedido.id_cliente.in_([c_cli1.id_cliente, c_cli2.id_cliente])).count()
        if pedidos_demo_existentes < 4:
            _create_demo_pedido(c_cli1, u_cajero, [(p1, 2), (p3, 1)], estado='Pendiente', estado_pago='Pendiente', metodo_pago='Efectivo')
            _create_demo_pedido(c_cli1, u_cajero, [(p2, 2)], estado='Pendiente', estado_pago='Pagado', metodo_pago='Tarjeta')
            _create_demo_pedido(c_cli2, u_cajero, [(p1, 1), (p2, 1)], estado='En Proceso', estado_pago='Pendiente', metodo_pago='Transferencia', requiere_produccion=True)
            _create_demo_pedido(c_cli2, u_cajero, [(p3, 3)], estado='Completado', estado_pago='Pagado', metodo_pago='Efectivo')

        db.session.commit()

        print('Demo seed completed successfully.')
        print('Credenciales demo:')
        print('  admin: demo_admin / DemoAdmin123!')
        print('  cajero: demo_cajero / DemoCaja123!')
        print('  cliente1: demo_cliente1 / DemoCliente123!')
        print('  cliente2: demo_cliente2 / DemoCliente123!')


if __name__ == '__main__':
    run()
