import hashlib
import random
import string

from core.config import app_settings
from schemas.users import UserRedis


def get_random_string(length=12):
    """Генерирует случайную строку."""
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def hash_password(password: str, salt: str = None):
    """Хеширует пароль."""
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac(
        app_settings.algorithm,
        password.encode(),
        salt.encode(),
        app_settings.hmac_iteration)
    return f"{salt}${enc.hex()}"


def validate_password(password: str, hashed_password: str):
    """Проверяет, что хеш пароля совпадает с хешем из БД."""
    salt = hashed_password.split("$")[0]
    return hash_password(password, salt) == hashed_password


def user_str(user):
    return {
        'id': user.id,
        'name': user.name,
        'is_active': 1 if user.is_active else 0
    }


def user_obj(user: dict) -> UserRedis:
    return UserRedis(
        name=user.get('name'),
        id=user.get('id'),
        is_active=True if user.get('is_active') else False
    )
