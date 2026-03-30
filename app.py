from flask import Flask, render_template, request, redirect, url_for, session

from modulos.usuarios import usuarios
from modulos.proveedores import proveedores
from modulos.productos import productos
from modulos.inventario import inventario
from modulos.ventas import ventas
from modulos.caja import caja
from modulos.reportes import reportes
from modulos.materiaprima import materiaprima
from modulos.recetas import recetas
from modulos.produccion import produccion
from modulos.categorias import categorias
from modulos.menu import menu
from modulos.compras import compras
from modulos.clientes import cliente

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'

app.register_blueprint(usuarios)
app.register_blueprint(proveedores)
app.register_blueprint(productos)
app.register_blueprint(inventario)
app.register_blueprint(ventas)
app.register_blueprint(caja)
app.register_blueprint(reportes)
app.register_blueprint(materiaprima)
app.register_blueprint(recetas)
app.register_blueprint(produccion)
app.register_blueprint(categorias)
app.register_blueprint(menu)
app.register_blueprint(compras)
app.register_blueprint(cliente)

# Redirige raíz a /index
@app.route('/')
def root():
    return redirect(url_for('index'))

# Pantalla de login en /index
@app.route('/index')
def index():
    return render_template('auth/index.html')

# Procesar login (simulado)
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    # Simulación: cualquier usuario/contraseña funciona
    if username and password:
        session['usuario'] = username
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

# Cerrar sesión
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

# Pantalla principal (dashboard)
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')




if __name__ == '__main__':
    app.run(debug=True)