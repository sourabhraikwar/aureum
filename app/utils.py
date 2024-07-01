# Helper functions
import base64
from datetime import datetime, timedelta
import os
from hashlib import sha256
from time import timezone

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from app.main import ALGORITHM, SECRET_KEY, db, oauth2_scheme
from app.models import TokenData, UserInDB


def get_password_hash(password: str) -> str:
    salt = os.urandom(32)
    key = sha256(password.encode("utf-8") + salt).digest()
    return base64.urlsafe_b64encode(salt + key).decode("utf-8")

# app/models.py


def verify_password(plain_password: str, stored_password: str) -> bool:
    try:
        decoded = base64.urlsafe_b64decode(stored_password)
        salt, key = decoded[:32], decoded[32:]
        new_key = sha256(plain_password.encode("utf-8") + salt).digest()
        return key == new_key
    except:
        return False


async def get_user(username: str):
    user = await db.users.find_one({"username": username})
    if user:
        return UserInDB(**user)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = timezone.now() + expires_delta
    else:
        expire = timezone.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
