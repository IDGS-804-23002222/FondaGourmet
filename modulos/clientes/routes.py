from flask import render_template, request, redirect, url_for, session
from flask import flash
import time 
from datetime import datetime
from . import cliente
from functools import wraps

def login_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Verifica si hay sesión de cliente activa
        if "cliente_email" not in session:
            flash("Debes iniciar sesión como cliente para continuar", "error")
            return redirect(url_for("cliente.login"))
        return func(*args, **kwargs)
    return wrapper

@cliente.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        usuarios = [
            {"email": "cliente@test.com", "password": "1234"}
        ]

        usuario = next((u for u in usuarios if u["email"] == email and u["password"] == password), None)

        if usuario:
            # Guardar sesión de cliente sin afectar la del admin
            session["cliente_email"] = email
            flash("Has iniciado sesión correctamente.", "success")
            return redirect(url_for("cliente.cliente_menu"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")

    return render_template("cliente/login.html")

@cliente.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")

        # Simulación:
        # Aquí solo mostrarías confirmación. No hay BD real.
        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("cliente.login"))

    return render_template("cliente/registro.html")

@cliente.route('/logout')
def logout():
    # Solo eliminar datos del cliente, no todo
    session.pop('cliente_email', None)
    session.pop('carrito', None)
    flash("Sesión de cliente cerrada", "success")
    return redirect(url_for("cliente.login"))

# ---------------------------
# MENÚ PRINCIPAL DEL CLIENTE
# ---------------------------
@cliente.route('/menu')
def cliente_menu():
    productos = [
        {"id": 1, "nombre": "Pizza Pepperoni", "descripcion": "Deliciosa pizza con pepperoni", "precio": 180},
        {"id": 2, "nombre": "Hamburguesa Gourmet", "descripcion": "Carne Angus con queso cheddar", "precio": 150},
        {"id": 3, "nombre": "Pasta Alfredo", "descripcion": "Pasta con salsa cremosa Alfredo", "precio": 160},
    ]
    return render_template("cliente/menu.html", productos=productos)

# ---------------------------
# VER CARRITO
# ---------------------------
@cliente.route('/carrito')
@login_requerido
def ver_carrito():
    carrito = session.get("carrito", [])
    total = sum(item["precio"] * item["cantidad"] for item in carrito)

    return render_template(
        "cliente/carrito.html",
        carrito=carrito,
        total=total
    )

# ---------------------------
# AGREGAR AL CARRITO
# ---------------------------
@cliente.route('/agregar_carrito/<int:id>')
@login_requerido
def agregar_carrito(id):
    productos = {
        1: {"id": 1, "nombre": "Pizza Pepperoni", "precio": 180},
        2: {"id": 2, "nombre": "Hamburguesa Gourmet", "precio": 150},
        3: {"id": 3, "nombre": "Pasta Alfredo", "precio": 160},
    }

    producto = productos.get(id)
    if not producto:
        return redirect(url_for("cliente.cliente_menu"))

    carrito = session.get("carrito", [])

    for item in carrito:
        if item["id"] == id:
            item["cantidad"] += 1
            break
    else:
        carrito.append({
            "id": id,
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": 1
        })

    session["carrito"] = carrito

    return redirect(url_for("cliente.ver_carrito"))
    productos = {
        1: {"id": 1, "nombre": "Pizza Pepperoni", "precio": 180},
        2: {"id": 2, "nombre": "Hamburguesa Gourmet", "precio": 150},
        3: {"id": 3, "nombre": "Pasta Alfredo", "precio": 160},
    }

    producto = productos.get(id)
    if not producto:
        return redirect(url_for("cliente.cliente_menu"))

    carrito = session.get("carrito", [])


    if not isinstance(carrito, list):
        carrito = []

    for item in carrito:
        if item["id"] == id:
            item["cantidad"] += 1
            break
    else:
        carrito.append({
            "id": producto["id"],
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": 1
        })

    session["carrito"] = carrito

    return redirect(url_for("cliente.ver_carrito"))
    productos = {
        1: {"id": 1, "nombre": "Pizza Pepperoni", "precio": 180},
        2: {"id": 2, "nombre": "Hamburguesa Gourmet", "precio": 150},
        3: {"id": 3, "nombre": "Pasta Alfredo", "precio": 160},
    }

    producto = productos.get(id)
    if not producto:
        return redirect(url_for("cliente.cliente_menu"))

    carrito = session.get("carrito", [])

    for item in carrito:
        if item["id"] == id:
            item["cantidad"] += 1
            break
    else:
        carrito.append({"id": id, "nombre": producto["nombre"], "precio": producto["precio"], "cantidad": 1})

    session["carrito"] = carrito

    return redirect(url_for("cliente.ver_carrito"))

# ---------------------------
# ACTUALIZAR CARRITO
# ---------------------------
@cliente.route('/actualizar_carrito', methods=['POST'])
@login_requerido
def actualizar_carrito():
    carrito = session.get("carrito", [])

    for item in carrito:
        key = f"cantidad_{item['id']}"
        if key in request.form:
            nueva_cantidad = int(request.form[key])

            if nueva_cantidad <= 0:
                # marcar para eliminar
                item["cantidad"] = 0
            else:
                item["cantidad"] = nueva_cantidad

    # eliminar productos con cantidad 0
    carrito = [item for item in carrito if item["cantidad"] > 0]

    session["carrito"] = carrito

    flash("Carrito actualizado", "success")
    return redirect(url_for("cliente.ver_carrito"))

# ---------------------------
# ELIMINAR DEL CARRITO
# ---------------------------
@cliente.route('/eliminar_carrito/<int:id>')
@login_requerido
def eliminar_carrito(id):
    carrito = session.get("carrito", [])

    carrito = [item for item in carrito if item["id"] != id]

    session["carrito"] = carrito
    flash("Producto eliminado del carrito", "success")

    return redirect(url_for("cliente.ver_carrito"))

# ---------------------------
# CHECKOUT
# ---------------------------
@cliente.route('/checkout')
@login_requerido
def checkout():
    carrito = session.get("carrito", [])
    total = sum(item["precio"] * item["cantidad"] for item in carrito)
    return render_template("cliente/checkout.html", carrito=carrito, total=total)

@cliente.route('/realizar_pedido', methods=['POST'])
@login_requerido
def realizar_pedido():
    carrito = session.get("carrito", [])

    if not carrito:
        flash("El carrito está vacío", "error")
        return redirect(url_for("cliente.checkout"))

    # Datos desde el formulario
    nombre = request.form.get("nombre")
    telefono = request.form.get("telefono")
    direccion = request.form.get("direccion")
    notas = request.form.get("notas")

    # Calcular total
    total = sum(item["precio"] * item["cantidad"] for item in carrito)

    # Crear ID único
    nuevo_id = int(time.time())

    # Crear pedido con productos completos
    pedido = {
        "id": nuevo_id,
        "nombre": nombre,
        "telefono": telefono,
        "direccion": direccion,
        "notas": notas,
        "total": total,
        "estado": "Pendiente",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "productos": carrito.copy()   # 👈 AQUÍ VA LA LISTA COMPLETA
    }

    # Guardar
    pedidos = session.get("pedidos", [])
    pedidos.append(pedido)
    session["pedidos"] = pedidos

    # Vaciar carrito (solo después de guardar el pedido)
    session["carrito"] = []

    return redirect(url_for("cliente.cliente_confirmacion", pedido_id=nuevo_id))

# ---------------------------
# CONFIRMAR PEDIDO
# ---------------------------
@cliente.route('/confirmacion/<int:pedido_id>')
@login_requerido
def cliente_confirmacion(pedido_id):
    pedidos = session.get('pedidos', [])

    # Buscar el pedido REAL por ID
    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)

    if not pedido:
        flash('Pedido no encontrado', 'error')
        return redirect(url_for('cliente.cliente_menu'))

    return render_template('cliente/confirmacion.html', pedido=pedido)

# ---------------------------
# CANCELAR PEDIDO
# ---------------------------
@cliente.route('/cancelar_pedido/<int:pedido_id>')
@login_requerido
def cancelar_pedido(pedido_id):
    pedidos = session.get('pedidos', [])

    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)

    if not pedido:
        flash("Pedido no encontrado", "error")
        return redirect(url_for('cliente.cliente_menu'))

    return render_template("cliente/cancelar_pedido.html", pedido=pedido)

@cliente.route('/cancelar_pedido_confirmar/<int:pedido_id>', methods=["POST"])
@login_requerido
def cancelar_pedido_confirmar(pedido_id):
    pedidos = session.get('pedidos', [])

    for pedido in pedidos:
        if pedido['id'] == pedido_id:
            pedido['estado'] = 'Cancelado'
            session['pedidos'] = pedidos
            flash("Pedido cancelado correctamente", "success")
            break
    else:
        flash("Pedido no encontrado", "error")

    return redirect(url_for('cliente.cliente_confirmacion', pedido_id=pedido_id))

# ---------------------------
# CONSULTAR PEDIDOS
# ---------------------------
@cliente.route('/consultar_pedidos')
@login_requerido
def cliente_consultar_pedidos():
    # Ejemplo de historial
    pedidos = [
        {"id": 1, "fecha": "2024-11-28", "total": 420},
        {"id": 2, "fecha": "2024-12-02", "total": 180},
    ]
    return render_template("cliente/consultar_pedidos.html", pedidos=pedidos)

# ---------------------------
# DETALLE PEDIDO
# ---------------------------
@cliente.route('/detalle_pedido/<int:id>')
@login_requerido
def detalle_pedido(id):
    pedidos = session.get("pedidos", [])

    # Buscar el pedido en la lista guardada en sesión
    pedido = next((p for p in pedidos if p["id"] == id), None)

    if not pedido:
        flash("Pedido no encontrado", "error")
        return redirect(url_for("cliente.cliente_menu"))

    return render_template("cliente/detalle_pedido.html", pedido=pedido)

# ---------------------------
# CANCELAR PEDIDO
# ---------------------------
@cliente.route('/cancelar_pedido/<int:id>')
@login_requerido
def cliente_cancelar_pedido(id):
    return render_template("cliente/cancelar_pedido.html", id=id)