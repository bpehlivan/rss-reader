from passlib.hash import pbkdf2_sha256

from app.models import User


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(plain_password: str, user: User) -> bool:
    return pbkdf2_sha256.verify(plain_password, user.password)
