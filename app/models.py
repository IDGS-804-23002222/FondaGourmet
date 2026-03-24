from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, event
from sqlalchemy.ext.hybrid import hybrid_property
import datetime 

db = SQLAlchemy()
from sqlalchemy import CheckConstraint

class Persona(db.Model):
    __tablename__ = 'personas'
    id_persona = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_p = db.Column(db.String(50), nullable=False)
    apellido_m = db.Column(db.String(50))
    telefono = db.Column(db.String(10), unique=True, nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    direccion = db.Column(db.String(200))
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False, format='%d-%m-%y %H:%M:%S')

    __table_args__ = (
        CheckConstraint("telefono REGEXP '^[0-9]{10}$'", name='check_telefono'),
        CheckConstraint("correo REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'", name='check_correo_empleado'),
    )

class Rol(db.Model):
    __tablename__ = 'roles'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    
    __table_args__ = (
        CheckConstraint("nombre IN ('Administrador', 'Cajero', 'Cliente', 'Cocinero', 'Dueño')", name='check_nombre_rol'),
    )

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False, format='%d-%m-%y %H:%M:%S')
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)

    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))
     
class Empleado(db.Model):
    __tablename__ = 'empleados'
    id_empleado = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id_persona'), nullable=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('empleado', uselist=False, cascade="all, delete-orphan"))
    persona = db.relationship('Persona', backref=db.backref('empleado', uselist=False, cascade="all, delete-orphan"))
    
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id_persona'), nullable=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('cliente', uselist=False, cascade="all, delete-orphan"))
    persona = db.relationship('Persona', backref=db.backref('cliente', uselist=False, cascade="all, delete-orphan"))
      
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id_proveedor = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id_persona'), nullable=False)
    
    persona = db.relationship('Persona', backref=db.backref('proveedor', uselist=False, cascade="all, delete-orphan"))
      
class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    
class MateriaPrima(db.Model):
    __tablename__ = 'materias_primas'
    id_materia = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    unidad_medida = db.Column(db.String(20), nullable=False)
    stock_actual = db.Column(db.Float, default=0, nullable=False)
    stock_minimo = db.Column(db.Float, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    porcentaje_merma = db.Column(db.Float, default=0, nullable=False)
    factor_conversion = db.Column(db.Float, default=1, nullable=False)
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)

    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'), nullable=False)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'), nullable=False)

    categoria = db.relationship('Categoria', backref=db.backref('materias_primas', lazy=True))
    proveedor = db.relationship('Proveedor', backref=db.backref('materias_primas', lazy=True))
    
    __table_args__ = (
        CheckConstraint('precio >= 0', name='check_precio_no_negativo'),
        CheckConstraint('stock_actual >= 0', name='check_stock_actual_no_negativo'),
        CheckConstraint('stock_minimo >= 0', name='check_stock_minimo_no_negativo'),
        CheckConstraint('porcentaje_merma >= 0 AND porcentaje_merma <= 100', name='check_porcentaje_merma'),
        CheckConstraint('factor_conversion > 0', name='check_factor_conversion_positivo'),
        CheckConstraint("unidad_medida IN ('kg', 'g', 'l', 'ml', 'pz')", name='check_unidad_medida')
    )

class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock_actual = db.Column(db.Float, default=0, nullable=False)
    stock_minimo = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(255))
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'), nullable=False)
   
    categoria = db.relationship('Categoria', backref=db.backref('productos', lazy=True))

    __table_args__ = (
        CheckConstraint('precio >= 0', name='check_precio_no_negativo'),
        CheckConstraint('stock_actual >= 0', name='check_stock_actual_no_negativo'),
        CheckConstraint('stock_minimo >= 0', name='check_stock_minimo_no_negativo'),
        CheckConstraint("imagen REGEXP '^(https?://.*\\.(?:png|jpg|jpeg|gif|svg))$'", name='check_formato_imagen'),
    )   

class Receta(db.Model):
    __tablename__ = 'recetas'
    id_receta = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False, format='%d-%m-%y %H:%M:%S')
    
    detalles = db.relationship('RecetaDetalle', back_populates='receta', cascade="all, delete-orphan")
    producto = db.relationship('Producto', backref=db.backref('recetas', lazy=True))

    # Método para calcular el costo total de la receta
    @hybrid_property
    def costo_total(self):
        return sum(detalle.cantidad * detalle.materia_prima.precio for detalle in self.detalles)
    
    # Método para calcular la utilidad de la receta
    @hybrid_property
    def utilidad(self):
        return self.producto.precio - self.costo_total if self.producto else 0

class RecetaDetalle(db.Model):
    __tablename__ = 'receta_detalle'
    id_detalle = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Float, nullable=False)
    id_receta = db.Column(db.Integer, db.ForeignKey('recetas.id_receta'), nullable=False)
    id_materia = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materia'), nullable=False)

    receta = db.relationship('Receta', backref=db.backref('detalles', lazy=True))
    materia_prima = db.relationship('MateriaPrima', backref=db.backref('detalle_recetas', lazy=True))
      
class Produccion(db.Model):
    __tablename__ = 'producciones'
    id_produccion = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, format='%d-%m-%y %H:%M:%S')
    estado = db.Column(db.String(50), nullable=False, default='Solicitada')
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False, format='%d-%m-%y %H:%M:%S')
    
    detalles = db.relationship('DetalleProduccion', back_populates='produccion', cascade="all, delete-orphan")
    usuario = db.relationship('Usuario', backref=db.backref('producciones', lazy=True))

    __table_args__ = (
        CheckConstraint("estado IN ('Solicitada', 'En Proceso', 'Completada')", name='check_estado_produccion'),
    )

class DetalleProduccion(db.Model):
    __tablename__ = 'detalle_produccion'
    id_detalle = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Float, nullable=False)
    id_produccion = db.Column(db.Integer, db.ForeignKey('producciones.id_produccion'), nullable=False)
    id_materia = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materia'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)

    produccion = db.relationship('Produccion', back_populates='detalles')
    materia_prima = db.relationship('MateriaPrima', backref=db.backref('detalle_producciones', lazy=True))
    producto = db.relationship('Producto', backref=db.backref('detalle_producciones', lazy=True))

class Compra(db.Model):
    __tablename__ = 'compras'
    id_compra = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, format='%d-%m-%y %H:%M:%S')
    total = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False, format='%d-%m-%y %H:%M:%S')
    
    proveedor = db.relationship('Proveedor', backref=db.backref('compras', lazy=True))
    detalles = db.relationship('DetalleCompra', back_populates='compra', cascade="all, delete-orphan")
    usuario = db.relationship('Usuario', backref=db.backref('compras', lazy=True))
    
    __table_args__ = (
        CheckConstraint("metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia')", name='check_metodo_pago'),
        CheckConstraint('total >= 0', name='check_total_no_negativo'),
    )
    
    def calcular_total(self):
        self.total = sum(detalle.subtotal for detalle in self.detalles)
    
class DetalleCompra(db.Model):
    __tablename__ = 'detalle_compra'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_compra = db.Column(db.Integer, db.ForeignKey('compras.id_compra'), nullable=False)
    id_materia = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materia'), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    precio_u = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
  
    compra = db.relationship('Compra', back_populates='detalles')
    materia_prima = db.relationship('MateriaPrima', backref=db.backref('detalle_compras', lazy=True))
    
    __table_args__ = (
        CheckConstraint('cantidad > 0', name='check_cantidad_positiva'),
        CheckConstraint('precio_u >= 0', name='check_precio_u_no_negativo'),
        CheckConstraint('subtotal >= 0', name='check_subtotal_no_negativo'),
    )
    
    def calcular_subtotal(self):
        self.subtotal = self.cantidad * self.precio_u
    
class Venta(db.Model):
    __tablename__ = 'ventas'
    id_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, format='%d-%m-%y %H:%M:%S')
    total = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False, format='%d-%m-%y %H:%M:%S')

    usuario = db.relationship('Usuario', backref=db.backref('ventas', lazy=True))
    detalles = db.relationship('DetalleVenta', back_populates='venta', cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia')", name='check_metodo_pago_venta'),
        CheckConstraint('total >= 0', name='check_total_venta_no_negativo'),
    )
    
    def calcular_total(self):
        self.total = sum(detalle.subtotal for detalle in self.detalles)
    
class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id_detalle = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    id_venta = db.Column(db.Integer, db.ForeignKey('ventas.id_venta'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    
    venta = db.relationship('Venta', back_populates='detalles')
    producto= db.relationship('Producto', backref=db.backref('detalle_ventas', lazy=True))
    
    __table_args__ = (
        CheckConstraint('cantidad > 0', name='check_cantidad_venta_positiva'),
        CheckConstraint('subtotal >= 0', name='check_subtotal_venta_no_negativo'),
    )
    
    def calcular_subtotal(self):
        self.subtotal = self.cantidad * self.producto.precio

class Carrito(db.Model):
    __tablename__ = 'carritos'
    id_carrito = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False, format='%d-%m-%y %H:%M:%S')
    estado = db.Column(db.String(20), nullable=False, default='Abierto')
    
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)
    
    Cliente = db.relationship('Cliente', backref=db.backref('carrito', lazy=True))
    detalles = db.relationship('DetalleCarrito', backref='carrito', lazy=True, cascade="all, delete-orphan")
    
class DetalleCarrito(db.Model):
    __tablename__ = 'detalle_carrito'
    id_detalle = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carritos.id_carrito'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)

    carrito = db.relationship('Carrito', backref=db.backref('detalles'))
    producto = db.relationship('Producto')

    __table_args__ = (
        CheckConstraint('cantidad > 0', name='check_cantidad_carrito_positiva'),
        CheckConstraint('subtotal >= 0', name='check_subtotal_carrito_no_negativo'),
    )
    
    def calcular_subtotal(self):
        self.subtotal = self.cantidad * self.producto.precio

class Caja(db.Model):
    __tablename__ = 'caja'
    id_caja = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, format='%d-%m-%y %H:%M:%S')
    monto_inicial = db.Column(db.Float, nullable=False)
    monto_final = db.Column(db.Float, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='Abierta')
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('cajas', lazy=True))
    movimientos = db.relationship('MovimientoCaja', backref='caja', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("estado IN ('Abierta', 'Cerrada')", name='check_estado_caja'),
        CheckConstraint('monto_inicial >= 0', name='check_monto_inicial_no_negativo'),
        CheckConstraint('monto_final >= 0', name='check_monto_final_no_negativo'),
    )

class MovimientoCaja(db.Model):
    __tablename__ = 'movimientos_caja'
    id_movimiento = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, format='%d-%m-%y %H:%M:%S')
    tipo = db.Column(db.String(20), nullable=False)  # Ingreso o Egreso
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)
    id_caja = db.Column(db.Integer, db.ForeignKey('caja.id_caja'), nullable=False)

    caja = db.relationship('Caja', backref=db.backref('movimientos', lazy=True))

    __table_args__ = (
        CheckConstraint("tipo IN ('Ingreso', 'Egreso')", name='check_tipo_movimiento'),
        CheckConstraint('monto >= 0', name='check_monto_movimiento_no_negativo'),
    )
    
    def aplicar_movimiento(self):
        if self.tipo == 'Ingreso':
            self.caja.monto_final = (self.caja.monto_final or self.caja.monto_inicial) + self.monto
        elif self.tipo == 'Egreso':
            self.caja.monto_final = (self.caja.monto_final or self.caja.monto_inicial) - self.monto   
    
# Conexión automática de eventos sqlalchemy para automatizar

# Actualización de stock al crear una compra
@event.listens_for(Compra, 'after_insert')
def actualizar_stock_compra(mapper, connection, target):
    for detalle in target.detalles:
        materia = detalle.materia_prima
        cantidad_real = detalle.cantidad * materia.factor_conversion
        materia.stock_actual += cantidad_real * (1 + materia.porcentaje_merma / 100)

# Actualización de stock al crear una producción
@event.listens_for(Produccion, 'after_insert')
def aplicar_produccion(mapper, connection, target):
    for detalle in target.detalles:
        materia = detalle.materia_prima
        materia.stock_actual -= detalle.cantidad
        detalle.producto.stock_actual += detalle.cantidad
    
# Actualización de stock al crear una venta
@event.listens_for(Venta, 'after_insert')
def aplicar_venta(mapper, connection, target):
    for detalle in target.detalles:
        detalle.producto.stock_actual -= detalle.cantidad