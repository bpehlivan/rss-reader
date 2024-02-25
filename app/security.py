from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.models import User, get_db_session
from settings import settings


# see for reference: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(
    db_session: Annotated[Session, Depends(get_db_session)],
    username: str,
    password: str,
) -> User | None:
    statement = select(User).where(User.username == username)
    results = db_session.exec(statement)
    user: User | None = results.first()

    if user and verify_password(password, user.password):
        return user
    return


def create_access_token(username: str):
    token_expires_delta = timedelta(
        minutes=settings.access_token_expire_minutes,
    )
    expire = datetime.now(timezone.utc) + token_expires_delta
    to_encode = {"sub": username, "exp": expire}

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def get_current_user(
    db_session: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.secret,
            algorithms=[settings.jwt_algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    statement = select(User).where(User.username == username)
    results = db_session.exec(statement)
    user = results.first()

    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
