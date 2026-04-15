import os
from sqlalchemy import create_engine


def _load_env_config_file():
    """Carga variables desde .env_config si existe (sin pisar las ya exportadas)."""
    env_path = os.path.join(os.path.dirname(__file__), '.env_config')
    if not os.path.exists(env_path):
        return

    with open(env_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_env_config_file()

class Config(object):
    SECRET_KEY = 'Clave_Secreta'
    SESSION_COOKIE_SECURE = False
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # 3MB max upload size
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = str(os.getenv('MAIL_USE_TLS', 'true')).lower() in ('1', 'true', 'yes', 'on')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@fondagourmet.local')
    # Google reCAPTCHA v2 checkbox. Defaults are test keys from Google.
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')
    RECAPTCHA_OPTIONS = {'theme': 'light'}



class DevelopmentConfig(Config):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:karlamtz233@localhost/fonda'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:23010@localhost/fonda'
    SQLALCHEMY_TRACK_MODIFICATIONS = False