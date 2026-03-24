from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pymongo import MongoClient

db = SQLAlchemy()
migrate = Migrate()
mongo_client = None

def init_extensions(app):
    global mongo_client
    db.init_app(app)
    migrate.init_app(app, db)
    
    # MongoDB
    mongo_client = MongoClient(app.config['MONGO_URI'])
    app.mongo = mongo_client.get_database("fonda")  # base de datos MongoDB