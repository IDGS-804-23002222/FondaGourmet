from pymongo import MongoClient
mongo_client = None

def init_extensions(app):
    global mongo_client
    mongo_uri = app.config.get('MONGO_URI') or 'mongodb://localhost:27017/fondaGourmet'

    try:
        mongo_client = MongoClient(mongo_uri)
        app.mongo = mongo_client.get_database('fondaGourmet')
        app.mongo_client = mongo_client
    except Exception as exc:
        app.mongo = None
        app.mongo_client = None
        app.logger.error(f'No fue posible inicializar MongoDB: {exc}')