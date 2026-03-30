import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_login import LoginManager, current_user  # Solo flask_login
from config import DevelopmentConfig
from models import db, Usuario, Rol
from auth.routes import auth
from dashboard.routes import dashboard
from ventas.routes import ventas
from produccion.routes import produccion
from tienda.routes import tienda
from usuarios.routes import usuarios

migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()  # Inicializar LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    # Configuración adicional
    app.config['REMEMBER_COOKIE_DURATION'] = 30 * 24 * 3600  # 30 días
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configurar LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Vista para login
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # User loader para flask_login
    @login_manager.user_loader
    def load_user(user_id):
        """Carga el usuario desde la base de datos"""
        try:
            return Usuario.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Error loading user {user_id}: {str(e)}")
            return None
    
    # Registrar blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    app.register_blueprint(ventas, url_prefix='/ventas')
    app.register_blueprint(produccion, url_prefix='/produccion')
    app.register_blueprint(tienda, url_prefix='/tienda')
    app.register_blueprint(usuarios, url_prefix='/usuarios')
    
    # Configurar logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=3)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # 🚨 Errores
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f'404: {request.url}')
        return render_template('404.html'), 404
    
    # Context processor para tener current_user disponible en todas las plantillas
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    
    # 🏠 Home
    @app.route("/")
    def index():
        return render_template("index.html")
    
    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)