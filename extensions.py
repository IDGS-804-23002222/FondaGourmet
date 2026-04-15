from db_mongo import init_mongo


def init_extensions(app):
    # Wrapper legacy para mantener compatibilidad con imports antiguos.
    init_mongo(app)