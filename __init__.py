from flask import Flask
from .config import Config
from .extensions import db, migrate, init_extensions

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    init_extensions(app)
    
    # Blueprint login
    from .blueprints.auth import auth_bp
    from .blueprints.categorias import categorias_bp
    from .blueprints.materias_primas import materias_primas_bp
    from .blueprints.productos import productos_bp
    from .blueprints.producciones import producciones_bp
    from .blueprints.reportes import reportes_bp
    from .blueprints.empleados import empleados_bp
    from .blueprints.clientes import clientes_bp
    from .blueprints.proveedores import proveedores_bp
    from .blueprints.inventarios import inventarios_bp
    from .blueprints.ventas import ventas_bp
    from .blueprints.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(categorias_bp, url_prefix='/categorias')
    app.register_blueprint(materias_primas_bp, url_prefix='/materias-primas')
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(producciones_bp, url_prefix='/producciones')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    app.register_blueprint(empleados_bp, url_prefix='/empleados')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(proveedores_bp, url_prefix='/proveedores')
    app.register_blueprint(inventarios_bp, url_prefix='/inventarios')
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app