import logging

from flask import current_app
from pymongo import MongoClient
from werkzeug.local import LocalProxy


def init_mongo(app):
    mongo_uri = app.config.get('MONGO_URI') or 'mongodb://localhost:27017/fondaGourmet'
    mongo_db_name = app.config.get('MONGO_DB_NAME', 'fondaGourmet')

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2500)
        client.admin.command('ping')
        app.mongo_client = client
        app.mongo = client.get_database(mongo_db_name)
    except Exception as e:
        logging.warning(f'Mongo deshabilitado al iniciar la app: {e}')
        app.mongo_client = None
        app.mongo = None


def _get_mongo_db():
    return current_app.mongo


mongo_db = LocalProxy(_get_mongo_db)