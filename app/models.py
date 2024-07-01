# app/models.py

from pydantic import BaseModel, Field
from bson import ObjectId


class User(BaseModel):
    username: str
    email: str
    full_name: str = None
    disabled: bool = False


class UserInDB(User):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None
