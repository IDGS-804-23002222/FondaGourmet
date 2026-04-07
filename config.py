import os
from sqlalchemy import create_engine

class Config(object):
    SECRET_KEY = 'Clave_Secreta'
    SESSION_COOKIE_SECURE = False
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # 3MB max upload size
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}



class DevelopmentConfig(Config):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:karlamtz233@localhost/fonda'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:23010@localhost/fonda'
    SQLALCHEMY_TRACK_MODIFICATIONS = False