from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

_fernet = None


def _get_fernet():
    global _fernet
    if _fernet is None:
        _fernet = Fernet(settings.FIELD_ENCRYPTION_KEY)
    return _fernet


def encrypt(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    try:
        return _get_fernet().decrypt(value.encode()).decode()
    except InvalidToken:
        raise ValueError('Não foi possível decriptar o valor — FIELD_ENCRYPTION_KEY mudou ou o dado está corrompido.')
