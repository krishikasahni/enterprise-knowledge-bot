from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
ALGORITHM = "HS256"

# Passwords stored as plain text here, hashed on first use
FAKE_USERS_DB = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "user":  {"username": "user",  "password": "user123",  "role": "viewer"},
}


class User(BaseModel):
    username: str
    role: str


def authenticate_user(username: str, password: str):
    user = FAKE_USERS_DB.get(username)
    if not user or user["password"] != password:
        return None
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role", "viewer")
        if not username:
            raise exc
        return User(username=username, role=role)
    except JWTError:
        raise exc


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
