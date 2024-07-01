from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from app.models import User, UserCreate, UserInDB
from bson import ObjectId

app = FastAPI(
    title="FastAPI with MongoDB",
    description="This is a FastAPI application with MongoDB integration.",
    version="1.0.0",
    contact={
        "name": "Sourabh Raikwar",
        "email": "sourabhraikwar11111@example.com",
    },
)

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.aureus


@app.post("/users/")
async def create_user(user: UserCreate):
    user_dict = user.model_dump()
    user_in_db = UserInDB(**user_dict)
    result = await db.users.insert_one(user_in_db.model_dump(by_alias=True))
    user_in_db.id = result.inserted_id
    return User(**user_in_db.model_dump(by_alias=True))


@app.get("/users/")
async def read_users():
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)


@app.put("/users/{user_id}")
async def update_user(user_id: str, user: UserCreate):
    update_data = user.model_dump(exclude_unset=True)
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


# Start the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
