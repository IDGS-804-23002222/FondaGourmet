import os
from sqlalchemy import create_engine

class Config(object):
    SECRET_KEY = 'Clave_Secreta'
    SESSION_COOKIE_SECURE = False
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # 3MB max upload size
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    # Google reCAPTCHA v2 checkbox. Defaults are test keys from Google.
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')
    RECAPTCHA_OPTIONS = {'theme': 'light'}



class DevelopmentConfig(Config):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:karlamtz233@localhost/fonda'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:23010@localhost/fonda'
    SQLALCHEMY_TRACK_MODIFICATIONS = False