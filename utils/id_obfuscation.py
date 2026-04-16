from itsdangerous import BadSignature, URLSafeSerializer
from flask import current_app


_DEFAULT_SALT = 'fonda.ids.v1'


def _serializer(salt=None):
    secret = current_app.config.get('SECRET_KEY') or 'Clave_Secreta'
    return URLSafeSerializer(secret_key=secret, salt=salt or _DEFAULT_SALT)


def encode_id(value, namespace='generic'):
    serializer = _serializer(salt=f'{_DEFAULT_SALT}.{namespace}')
    return serializer.dumps(int(value))


def decode_id(token, namespace='generic'):
    serializer = _serializer(salt=f'{_DEFAULT_SALT}.{namespace}')
    try:
        return int(serializer.loads(token))
    except (BadSignature, TypeError, ValueError):
        return None


def decode_or_int(value, namespace='generic'):
    # Backward-compatible: accepts plain numeric ids and signed tokens.
    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    if raw.isdigit():
        return int(raw)

    return decode_id(raw, namespace=namespace)
