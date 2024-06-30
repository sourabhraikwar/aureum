from typing import List

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from app.models import User, UserCreate, UserInDB

app = FastAPI()

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.test_database


@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    user_dict = user.dict()
    user_in_db = UserInDB(**user_dict)
    result = await db.users.insert_one(user_in_db.dict(by_alias=True))
    user_in_db.id = result.inserted_id
    return User(**user_in_db.dict(by_alias=True))


@app.get("/users/", response_model=List[User])
async def read_users():
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserCreate):
    update_data = user.dict(exclude_unset=True)
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    user_in_db = await db.users.find_one({"_id": ObjectId(user_id)})
    return User(**user_in_db)


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
