from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from typing import Optional

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, *args):
        for v in args:
            if not ObjectId.is_valid(v):
                raise ValueError('Invalid objectid')
            return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema

class UserBase(BaseModel):
    username: str = Field(..., example="john_doe")
    email: EmailStr = Field(..., example="john.doe@example.com")

class UserCreate(UserBase):
    password: str = Field(..., example="secret_password")

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        json_encoders = {
            ObjectId: str
        }
