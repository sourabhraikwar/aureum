from typing import Any, Dict
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.constants import ACCESS_TOKEN_EXPIRE_MINUTES, db
from app.utils import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from .models import User, UserInDB, Token

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users/", response_model=User)
async def create_user(user: UserInDB):
    password = get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = password
    new_user = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    return User(**created_user)


@router.patch("/users/me", response_model=User)
async def update_user_partial(
    update_data: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    if len(update_data) == 0:
        raise HTTPException(status_code=400, detail="No update data provided")

    update_result = await db.users.update_one(
        {"username": current_user.username}, {"$set": update_data}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")

    updated_user = await db.users.find_one({"username": current_user.username})
    return User(**updated_user)


@router.put("/users/me", response_model=User)
async def update_user_full(
    user_update: UserInDB, current_user: User = Depends(get_current_user)
):
    update_data = user_update.model_dump(exclude={"password"})

    update_result = await db.users.replace_one(
        {"username": current_user.username}, update_data
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")

    updated_user = await db.users.find_one({"username": current_user.username})
    return User(**updated_user)


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user: User = Depends(get_current_user)):
    delete_result = await db.users.delete_one({"username": current_user.username})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"detail": "User deleted successfully"}
